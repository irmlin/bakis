import asyncio
import multiprocessing
import os
import queue
import shutil
import sys
import threading
import time
import traceback
import uuid
from multiprocessing import Queue
from typing import List, Dict, Any

import cv2
import numpy as np
from fastapi import UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..ml import WorkerMLInference
from ..models import Video, Accident
from ..models.enums import SourceStatus, AccidentType
from ..schemas import VideoCreate
from ..stream import WorkerStreamReader
from ..utilities.file_size import FileSize


class MediaService:

    # TODO add repository class
    def __init__(self):
        self.file_size_limit_bytes = FileSize.GB
        # Object for creating objects shared across processes
        self.__manager = multiprocessing.Manager()
        # TODO: could use a mp.Queue instead of Manager. Read streams on queue.Empty exception.
        #  This way, could maintain worker interface of read_queue -> on_done.
        self.__shared_sources_dict = self.__manager.dict()
        # Active websocket connections
        self.__connections: Dict[int, List[WebSocket]] = {}
        # self.__connections_lock = threading.Lock()
        self.__connections_lock = asyncio.Lock()
        # Queue of frames which have been inferred on and are ready for streaming
        self.__frames_queue = Queue(maxsize=500)
        self.__internal_state: Dict[int, Dict[str, Any]] = {}
        self.__sources_to_terminate = []
        self.__frames_buffer_size = 30
        self.__pipeline_fps = 32
        self.__active_source_id = None
        self.__alarm_score_thr = 0.8
        self.__alarm_timeout = 10 * 60
        # Whether streaming job is active
        self.__job_started = False

        # Workers
        self.__worker_ml_inference = WorkerMLInference(on_done=self.__put_processed_frames_to_queue,
                                                       batch_size=30)
        self.__worker_stream_reader = WorkerStreamReader(shared_sources_dict=self.__shared_sources_dict,
                                                         on_done=self.__worker_ml_inference.add)
        self.__worker_stream_reader.start()
        self.__worker_ml_inference.start()

    def upload_video(self, db: Session, video_create: VideoCreate, video_file: UploadFile):
        video_size_bytes = self.get_file_size(file=video_file)
        if video_size_bytes > self.file_size_limit_bytes:
            raise HTTPException(status_code=400,
                                detail=f'File size should not exceed'
                                       f' {round(FileSize.get_gb(self.file_size_limit_bytes), 3)} GB.')
        # TODO: add extension checks
        filename = uuid.uuid4()
        extname = os.path.splitext(video_file.filename)[1]

        video_file_name = f"{filename}{extname}"
        # TODO: fix this
        file_path = f'app/static/{video_file_name}'
        with open(file_path, "wb+") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        video = Video(title=video_create.title, description=video_create.description, file_path=file_path)
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    def delete_video(self, db: Session, video_id: int):
        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found.')
        if db_video.status == SourceStatus.PROCESSING:
            raise HTTPException(status_code=409, detail=f'Video with id {video_id} is currently being streamed,'
                                                        f' stop streaming first!')
        self.__delete_video_file(db_video.file_path)
        db.delete(db_video)
        db.commit()
        return {'detail': f'Video (id={video_id}) has been deleted.'}

    async def start_inference_task(self, db: Session, video_id: int):
        if not self.__job_started:
            asyncio.create_task(self.__stream_to_client(db))
            self.__job_started = True

        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found')
        if not self.__video_file_exists(db_video.file_path):
            raise HTTPException(status_code=404, detail=f'Video (id={video_id}) file not found')

        self.__worker_stream_reader.add_source(video_id, db_video.file_path)
        self.__internal_state[video_id] = {'q': queue.Queue(maxsize=1000),
                                           'ready': False,
                                           'last_sent_time': time.time(),
                                           'wait_time': 1 / self.__pipeline_fps,
                                           'last_alarm_time': None}
        self.__connections[video_id] = []
        db_video.status = SourceStatus.PROCESSING
        db.commit()
        return {'detail': f'Video (id={video_id}) is being streamed.'}

    async def accept_connection(self, source_id: int, websocket: WebSocket):
        if source_id not in self.__connections:
            return {'detail': f'Stream for source {source_id} is no longer available!.'}
        await websocket.accept()
        self.__connections[source_id].append(websocket)
        try:
            while True:
                # The websocket will be destroyed if this method terminates.
                # We can check for any incoming messages, while in the background
                # data is continuously sent to clients.
                await websocket.receive_text()
        except WebSocketDisconnect as e:
            # Handle any unexpected socket disconnect
            print('socket disconnected from client, but not removing from list yet', source_id)
            # async with self.__connections_lock:
            #     if source_id in self.__connections.keys():
            #         print('socket disconnected from client ', source_id)
            #         self.__connections[source_id].remove(websocket)

    async def __stream_to_client(self, db: Session):
        while 1:
            try:
                # TODO: what would happen, if less than buffer amount of frames get here, before stream terminates.
                # TODO: need to handle frame rate in other components as well
                source_id, enc_frame, result, success, frame_num = self.__frames_queue.get(block=False)
                self.__internal_state[source_id]['q'].put((source_id, enc_frame, result, success, frame_num),
                                                          block=False)
                self.__set_internal_q_buffer_ready(source_id)
            except queue.Empty:
                source_ids = list(self.__internal_state.keys())
                for source_id in source_ids:
                    if self.__frame_ready_for_stream(source_id=source_id):
                        await self.__handle_stream(source_id=source_id, db=db)
                # Allow other requests to process while no streams are running
                await asyncio.sleep(0.01)
            except queue.Full:
                # TODO. Duplicate code
                # TODO. Lost information about ended stream.
                print(f'Internal frames queue was full. Dropping frames!')
                source_ids = list(self.__internal_state.keys())
                for source_id in source_ids:
                    if self.__frame_ready_for_stream(source_id=source_id):
                        await self.__handle_stream(source_id=source_id, db=db)
                # Allow other requests to process while no streams are running
                await asyncio.sleep(0.01)
            except BaseException as e:
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{threading.current_thread().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

    async def __handle_stream(self, source_id: int, db: Session):
        try:
            _, enc_frame, scores, success, frame_num = self.__internal_state[source_id]['q'].get(block=False)
        except queue.Empty:
            return
        if success and enc_frame is not None:
            if source_id in self.__sources_to_terminate:
                # Client removed source, shouldn't process the leftover incoming frames for source.
                # Socket object will be destroyed, once success==False is received.
                print(f'not processing {source_id}, waiting for success=false')
                return
            self.__handle_accident(db=db, source_id=source_id, scores=scores, enc_frame=enc_frame)
            ws_to_remove = []
            # Make shallow copy. If new connection gets appended during the following loop, no unwanted behavior will occur.
            current_ws_conns = self.__connections[source_id][:]
            for ws in current_ws_conns:
                try:
                    await ws.send_bytes(enc_frame.tobytes())
                    await ws.send_json({'scores': scores.tolist()})
                    self.__internal_state[source_id]['last_sent_time'] = time.time()
                except (WebSocketDisconnect, RuntimeError):
                    ws_to_remove.append(ws)
            for ws in ws_to_remove:
                print('socket disconnected from client during streaming, removed from list', source_id)
                self.__connections[source_id].remove(ws)
        else:
            # Stream ended
            print('ENDED, ', source_id)
            if source_id not in self.__sources_to_terminate:
                db_video = self.get_video_by_id(db, source_id)
                db_video.status = SourceStatus.PROCESSED
                db.commit()
            del self.__internal_state[source_id]
            if source_id in self.__sources_to_terminate:
                self.__sources_to_terminate.remove(source_id)
            for ws in self.__connections[source_id]:
                try:
                    await ws.send_json({'source_id': source_id, 'detail': 'Video stream ended!'})
                    await ws.close()
                except WebSocketDisconnect:
                    # We will delete all source's connections regardless
                    pass
                except RuntimeError:
                    # Socket already disconnected from client
                    pass
            del self.__connections[source_id]

    def __handle_accident(self, db: Session, source_id: int, scores: np.ndarray, enc_frame: np.ndarray):
        if self.__check_accident(source_id=source_id, scores=scores):
            print('ACCIDENT, ', source_id)
            self.__save_accident(db=db, source_id=source_id, enc_frame=enc_frame)

    def __save_accident(self, db: Session, source_id: int, enc_frame: np.ndarray):
        image_name = f"{uuid.uuid4()}.jpg"
        image_path = f'app/static/{image_name}'
        img = cv2.imdecode(np.frombuffer(enc_frame, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imwrite(image_path, img)

        accident = Accident(type=AccidentType.CAR_CRASH, image_path=image_path, video_id=source_id)
        db.add(accident)
        db.commit()

    def __check_accident(self, source_id: int, scores: np.ndarray) -> bool:
        ts = time.time()
        if ((self.__internal_state[source_id]['last_alarm_time'] is not None and
             ts - self.__internal_state[source_id]['last_alarm_time'] < self.__alarm_timeout) or
                scores[0] < self.__alarm_score_thr):
            return False

        self.__internal_state[source_id]['last_alarm_time'] = ts
        return True

    def __frame_ready_for_stream(self, source_id: int):
        return (
                self.__internal_state[source_id]['ready'] and
                time.time() - self.__internal_state[source_id]['last_sent_time'] >= self.__internal_state[source_id][
                    'wait_time']
        )

    def __set_internal_q_buffer_ready(self, source_id):
        if self.__internal_state[source_id]['ready']:
            return
        if self.__internal_state[source_id]['q'].qsize() >= self.__frames_buffer_size:
            print(f'Buffered frames for source {source_id}, will start streaming!')
            self.__internal_state[source_id]['ready'] = True

    async def terminate_live_stream(self, db: Session, source_id: int):
        if source_id not in self.__connections.keys():
            print('fucker')
            return {'detail': f'Stream for source (id={source_id} )has already ended prior to this request!'}
        db_video = self.get_video_by_id(db, source_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Source with id {source_id} not found!')
        self.__worker_stream_reader.remove_source(source_id)

        self.__sources_to_terminate.append(source_id)
        db_video.status = SourceStatus.TERMINATED
        db.commit()

        return {'detail': f'Stream terminated for source (id={source_id})!'}

    def __put_processed_frames_to_queue(self, data):
        try:
            self.__frames_queue.put(data, block=True)
        except queue.Full:
            print(f'frames_queue is full! Element not added.')
            return

    @staticmethod
    def get_file_size(file: UploadFile) -> int:
        _ = file.file.seek(0, 2)
        file_size_bytes = file.file.tell()
        file.file.seek(0)
        return file_size_bytes

    def get_video_by_id(self, db: Session, video_id: int):
        return db.query(Video).filter(Video.id == video_id).first()

    def get_all_videos(self, db: Session):
        return db.query(Video).all()

    def get_live_videos(self, db: Session):
        return db.query(Video).filter(Video.status == SourceStatus.PROCESSING).all()

    def __video_file_exists(self, file_path: str):
        return os.path.exists(file_path)

    def __delete_video_file(self, file_path: str):
        if self.__video_file_exists(file_path):
            os.remove(file_path)
