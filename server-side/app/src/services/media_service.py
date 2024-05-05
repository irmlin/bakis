import asyncio
import multiprocessing
import os
import queue
import shutil
import sys
import threading
import time
import traceback
from multiprocessing import Queue
from multiprocessing.pool import Pool
from typing import List, Dict, Any

import cv2
import numpy as np
from fastapi import UploadFile, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session

from ..ml import WorkerMLInference
from ..email import EmailManager
from ..models import Video, Accident, Recipient, Setting
from ..models.enums import SourceStatus, AccidentType, accident_type_str_map
from ..schemas import VideoCreate
from ..stream import WorkerStreamReader
from ..utilities import FileSize, generate_file_path, get_adjusted_timezone


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
        # Queue of frames which have been inferred on and are ready for streaming
        self.__frames_queue = Queue(maxsize=100)
        self.__internal_state: Dict[int, Dict[str, Any]] = {}
        self.__sources_to_terminate = []
        self.__frames_buffer_size = 30
        self.__alarm_score_thr = 0.8
        self.__alarm_timeout = 10 * 60
        self.__video_cache_seconds = 5
        self.__accident_class_id = 0
        # Whether streaming job is active
        self.__job_started = False

        # Email
        self.__email_manager = EmailManager()

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
        extname = os.path.splitext(video_file.filename)[1]
        file_path = generate_file_path(extname)
        with open(file_path, "wb+") as buffer:
            shutil.copyfileobj(video_file.file, buffer)

        video_cap = cv2.VideoCapture(file_path)
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        video = Video(title=video_create.title, description=video_create.description, file_path=file_path,
                      fps=fps, width=width, height=height)
        video_cap.release()
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
                                           'last_fps_measure_time': time.time(),
                                           'wait_time': 1 / db_video.fps,
                                           'set_fps': db_video.fps,
                                           'num_sent': 0,
                                           'actual_fps': db_video.fps,
                                           'last_alarm_time': None,
                                           'video_fps': db_video.fps,
                                           'video_h': db_video.height,
                                           'video_w': db_video.width,
                                           'video_cache_num_frames': self.__video_cache_seconds * db_video.fps,
                                           'video_cache': []}
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
        except WebSocketDisconnect:
            print('socket disconnected from client, but not removing from list yet', source_id)

    async def __stream_to_client(self, db: Session):
        while 1:
            try:
                source_id, frame, enc_frame, scores, success = self.__frames_queue.get(block=False)
                # print(f'Internal frames q size: {self.__internal_state[source_id]["q"].qsize()}')
                self.__internal_state[source_id]['q'].put((source_id, frame, enc_frame, scores, success), block=False)
                self.__set_internal_q_buffer_ready(source_id)
            except queue.Empty:
                source_ids = list(self.__internal_state.keys())
                if len(source_ids) == 0:
                    await self.__rest()
                for source_id in source_ids:
                    if self.__frame_ready_for_stream(source_id=source_id):
                        await self.__handle_stream(source_id=source_id, db=db)
                # Allow other requests to process
                await asyncio.sleep(0.01)
            except queue.Full:
                # TODO. Duplicate code
                print(f'Internal frames queue was full. Dropping frames!')
                source_ids = list(self.__internal_state.keys())
                for source_id in source_ids:
                    if self.__frame_ready_for_stream(source_id=source_id):
                        await self.__handle_stream(source_id=source_id, db=db)
                # Allow other requests to process
                await asyncio.sleep(0.01)
            except BaseException as e:
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{threading.current_thread().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

    async def __handle_stream(self, source_id: int, db: Session):
        try:
            _, frame, enc_frame, scores, success = self.__internal_state[source_id]['q'].get(block=False)
        except queue.Empty:
            return
        if success and enc_frame is not None:
            if source_id in self.__sources_to_terminate:
                # Client removed source, shouldn't process the leftover incoming frames for source.
                # Socket object will be destroyed, once success==False is received.
                return
            self.__handle_video_cache(source_id=source_id, frame=frame)
            await self.__handle_accident(db=db, source_id=source_id, scores=scores, enc_frame=enc_frame)
            ws_to_remove = []
            # Make shallow copy. If new connection gets appended during the following loop, no unwanted behavior will occur.
            current_ws_conns = self.__connections[source_id][:]
            for ws in current_ws_conns:
                try:
                    await ws.send_bytes(enc_frame.tobytes())
                    await ws.send_json({'scores': scores.tolist()})
                except (WebSocketDisconnect, RuntimeError):
                    ws_to_remove.append(ws)
            self.__update_fps_info(source_id=source_id)
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

    async def __rest(self):
        print('resting')
        await asyncio.sleep(1)

    def __update_fps_info(self, source_id: int, qsize_min: int = 50):
        self.__internal_state[source_id]['last_sent_time'] = time.time()
        self.__internal_state[source_id]['num_sent'] += 1
        qsize = self.__internal_state[source_id]['q'].qsize()
        if self.__internal_state[source_id]['num_sent'] >= self.__internal_state[source_id]['video_fps']:
            cur_time = time.time()
            # Time taken to send video_fps number of frames
            time_taken = cur_time - self.__internal_state[source_id]['last_fps_measure_time']
            actual_fps = self.__internal_state[source_id]['video_fps'] / time_taken
            print(
                f'Actual FPS: {actual_fps}, time_taken: {time_taken}, set_fps: {self.__internal_state[source_id]["set_fps"]}')
            if actual_fps < self.__internal_state[source_id]['video_fps']:
                print(f'Made FPS Larger...........')
                self.__internal_state[source_id]['set_fps'] += 0.1
                self.__internal_state[source_id]['wait_time'] = 1 / (self.__internal_state[source_id]['set_fps'])
            elif (actual_fps > self.__internal_state[source_id]['video_fps'] or
                  qsize < qsize_min):
                print(f'Made FPS Smaller...........')
                self.__internal_state[source_id]['set_fps'] -= 0.1
                self.__internal_state[source_id]['wait_time'] = 1 / (self.__internal_state[source_id]['set_fps'])
            print(f"Internal q: {self.__internal_state[source_id]['q'].qsize()}")
            self.__internal_state[source_id]['num_sent'] = 0
            self.__internal_state[source_id]['actual_fps'] = actual_fps
            self.__internal_state[source_id]['last_fps_measure_time'] = cur_time

    def __handle_video_cache(self, source_id: int, frame: np.ndarray):
        current_cache_size = len(self.__internal_state[source_id]['video_cache'])
        if current_cache_size >= self.__internal_state[source_id]['video_cache_num_frames']:
            # TODO: probably not efficient, use dequeue
            self.__internal_state[source_id]['video_cache'] = self.__internal_state[source_id]['video_cache'][1:]
        self.__internal_state[source_id]['video_cache'].append(frame)

    async def __handle_accident(self, db: Session, source_id: int, scores: np.ndarray, enc_frame: np.ndarray):
        if self.__check_accident(source_id=source_id, scores=scores):
            print('ACCIDENT, ', source_id)
            await self.__save_accident(db=db, source_id=source_id, enc_frame=enc_frame, scores=scores)

    async def __save_accident(self, db: Session, source_id: int, enc_frame: np.ndarray, scores: np.ndarray):
        # Save image
        image_path = generate_file_path(ext='.jpg')
        img = cv2.imdecode(np.frombuffer(enc_frame, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imwrite(image_path, img)

        # Save video
        video_path = generate_file_path(ext='.mp4')
        fps, h, w = (self.__internal_state[source_id]['video_fps'], self.__internal_state[source_id]['video_h'],
                     self.__internal_state[source_id]['video_w'])
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        print(video_path, fourcc, fps, w, h, len(self.__internal_state[source_id]['video_cache']))
        out = cv2.VideoWriter(video_path, fourcc, int(fps), (int(w), int(h)))
        for frame in self.__internal_state[source_id]['video_cache']:
            out.write(frame)

        out.release()
        self.__internal_state[source_id]['video_cache'] = []

        accident = Accident(type=AccidentType.CAR_CRASH, image_path=image_path,
                            video_id=source_id, video_path=video_path, score=list(scores)[self.__accident_class_id])
        db.add(accident)
        db.commit()

        asyncio.create_task(self.__inform_about_accident(db=db, accident=accident))

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
            # print(f'Current frames queue size {self.__frames_queue.qsize()}')
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

    async def __inform_about_accident(self, db: Session, accident: Accident):
        recipients = self.__get_recipients(db=db)
        if recipients is None or len(recipients) == 0:
            return

        subject = self.__get_email_subject(accident=accident)
        body = self.__get_email_body(accident=accident)
        await self.__email_manager.send(recipients=recipients, subject=subject, body=body)

    def __get_email_body(self, accident: Accident) -> str:
        return f"""
        <html>
            <body>
                <p>
                    {accident_type_str_map[accident.type]} detected in video source {accident.video.title} at
                    {get_adjusted_timezone(accident.created_at)}! You may check detailed accident information 
                    <a href=http://localhost:3000/accidents>here</a>.
                </p>
            </body>
        </html>
        """

    def __get_email_subject(self, accident: Accident) -> str:
        return "Accident alert!"

    def __get_recipients(self, db: Session):
        return db.query(Recipient).all()

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
