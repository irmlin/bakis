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

from fastapi import UploadFile, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session

from ..models import Video
from ..models.enums import SourceStatus
from ..schemas import VideoCreate
from ..socket import WebSocketManager
from ..stream import WorkerStreamReader
from ..utilities.file_size import FileSize
from ..ml import WorkerMLInference


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
        self.__connections_lock = threading.Lock()
        # Queue of frames which have been inferred on and are ready for streaming
        self.__frames_queue = Queue(maxsize=500)
        self.__internal_queues: Dict[int, Dict[str, Any]] = {}
        self.__frames_buffer_size = 30
        self.__pipeline_fps = 15
        self.__active_source_id = None
        # Whether streaming job is active
        self.__job_started = False

        # Workers
        self.__worker_ml_inference = WorkerMLInference(on_done=self.__put_processed_frames_to_queue,
                                                       batch_size=5)
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

    async def start_inference_task(self, background_tasks: BackgroundTasks, db: Session, video_id: int):
        if not self.__job_started:
            # self.__job = threading.Thread(target=asyncio.create_task, args=(self.__stream_to_client(db),),
            #                               name='THREAD_read_processed_frames_from_queue')
            # self.__job.start()
            # background_tasks.add_task(self.__stream_to_client, db)
            # await asyncio.to_thread(self.__stream_to_client, db)
            # await asyncio.get_running_loop().run_in_executor(None, await self.__stream_to_client(db))
            asyncio.create_task(self.__stream_to_client(db))
            self.__job_started = True

        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found')
        if not self.__video_file_exists(db_video.file_path):
            raise HTTPException(status_code=404, detail=f'Video (id={video_id}) file not found')

        self.__worker_stream_reader.add_source(video_id, db_video.file_path)
        # TODO: removed hardcoded FPS
        self.__internal_queues[video_id] = {'q': queue.Queue(maxsize=500), 'ready': False,
                                            'last_sent_time': time.time(), 'wait_time': 1/self.__pipeline_fps}
        # Update source status
        db_video.status = SourceStatus.PROCESSING
        db.commit()
        return {'detail': f'Video (id={video_id}) is being streamed.'}

    async def accept_connection(self, source_id: int, websocket: WebSocket):
        await websocket.accept()
        with self.__connections_lock:
            if source_id in self.__connections.keys():
                self.__connections[source_id].append(websocket)
            else:
                self.__connections[source_id] = [websocket]
        try:
            while True:
                # The websocket will be destroyed if this method terminates.
                # We can check for any incoming messages, while in the background
                # data is continuously sent to clients.
                await websocket.receive_text()
        except WebSocketDisconnect as e:
            # Handle any unexpected socket disconnect
            with self.__connections_lock:
                if source_id in self.__connections.keys():
                    print('socket disconnected from client ', source_id)
                    self.__connections[source_id].remove(websocket)

    async def __stream_to_client(self, db: Session):
        while 1:
            try:
                source_id, enc_frame, result, success, frame_num = self.__frames_queue.get(block=False)
                print(f'SENDER0. {source_id} {success}')
                # self.__active_source_id = source_id
                self.__internal_queues[source_id]['q'].put((source_id, enc_frame, result, success, frame_num))
                self.__set_internal_q_buffer_ready(source_id)
            except queue.Empty:
                # if self.__active_source_id is not None:
                source_ids = list(self.__internal_queues.keys())
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
            _, enc_frame, result, success, frame_num = self.__internal_queues[source_id]['q'].get(block=False)
        except queue.Empty:
            print(f'Here! {source_id}')
            return
        with self.__connections_lock:
            print(f'SENDER. {source_id} {success}, frame was {enc_frame is not None}')
            if success and enc_frame is not None:
                if source_id in self.__connections.keys():
                    for ws in self.__connections[source_id]:
                        # TODO: MUST add WebSocketDisconnect catching here
                        print(f"PROCESSING: source {source_id}, frame {frame_num}. Internal queue: {self.__internal_queues[source_id]['q'].qsize()}. "
                              f"Success: {success}")
                        await ws.send_bytes(enc_frame.tobytes())
                        self.__internal_queues[source_id]['last_sent_time'] = time.time()
            else:
                # Stream ended
                print(f'HERE! {source_id}')
                db_video = self.get_video_by_id(db, source_id)
                db_video.status = SourceStatus.PROCESSED
                db.commit()
                del self.__internal_queues[source_id]
                if source_id in self.__connections.keys():
                    # Send stream end messages to all sockets, then close connection.
                    for ws in self.__connections[source_id]:
                        # TODO: MUST add WebSocketDisconnect catching here
                        await ws.send_json({'source_id': source_id, 'detail': 'Video stream ended!'})
                        await ws.close()
                    del self.__connections[source_id]

    def __frame_ready_for_stream(self, source_id: int):
        # Buffered frames have to be ready AND enough time passed since last sent frame to maintain FPS.
        # print(f"Wait time is {self.__internal_queues[source_id]['wait_time']}."
        #       f" Passed: {time.time() - self.__internal_queues[source_id]['last_sent_time']}")
        return (
            self.__internal_queues[source_id]['ready'] and
            time.time() - self.__internal_queues[source_id]['last_sent_time'] >= self.__internal_queues[source_id]['wait_time']
        )

    def __set_internal_q_buffer_ready(self, source_id):
        if self.__internal_queues[source_id]['ready']:
            return
        if self.__internal_queues[source_id]['q'].qsize() >= self.__frames_buffer_size:
            print(f'Buffered frames for source {source_id}, will start streaming!')
            self.__internal_queues[source_id]['ready'] = True

    async def terminate_live_stream(self, db: Session, source_id: int):
        print('connections before: ', self.__connections)
        db_video = self.get_video_by_id(db, source_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Source with id {source_id} not found!')
        self.__worker_stream_reader.remove_source(source_id)
        with self.__connections_lock:
            if source_id in self.__connections.keys():
                # Socket still open, means stream is being terminated. Otherwise, stream has ended previously.
                print('removing all sockets for source ', source_id)
                for ws in self.__connections[source_id]:
                    await ws.close()
                del self.__connections[source_id]
                db_video.status = SourceStatus.TERMINATED
                db.commit()

        return {'detail': f'Stream terminated for source (id={source_id})!'}

    def __put_processed_frames_to_queue(self, data):
        if self.__frames_queue.full():
            print(f'__frames_queue is full!')
            return

        self.__frames_queue.put(data)

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