import asyncio
import multiprocessing
import os
import queue
import shutil
import sys
import threading
import traceback
import uuid
from multiprocessing import Queue
from typing import List, Dict

from fastapi import UploadFile, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session

from ..models import Video
from ..models.enums import SourceStatus
from ..schemas import VideoCreate
from ..socket import WebSocketManager
from ..stream import WorkerStreamReader
from ..utilities.file_size import FileSize


class MediaService:

    # TODO add repository class
    def __init__(self):
        self.file_size_limit_bytes = FileSize.GB
        self.socket_manager = WebSocketManager()

        # Data traffic from processing job to app
        self.__connections: Dict[int, List[WebSocket]] = {}
        self.__connections_lock: asyncio.Lock = asyncio.Lock()
        self.__frames_queue = Queue(maxsize=500)
        self.__job = None
        self.__job_started = False

        # Data traffic from app to processing job
        self.__manager = multiprocessing.Manager()
        self.__shared_sources_dict = self.__manager.dict()
        self.__worker_stream_reader = WorkerStreamReader(shared_sources_dict=self.__shared_sources_dict,
                                                         on_done=self.__frames_queue.put)

        self.__worker_stream_reader.start()

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
            # self.__job = threading.Thread(target=asyncio.run, args=(self.__stream_to_client(db),),
            #                               name='THREAD_read_processed_frames_from_queue')
            # self.__job.start()
            print('before adding')
            background_tasks.add_task(self.__stream_to_client, db)
            print('after adding')
            self.__job_started = True
        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found')
        if not self.__video_file_exists(db_video.file_path):
            raise HTTPException(status_code=404, detail=f'Video (id={video_id}) file not found')

        self.__worker_stream_reader.add_source(video_id, db_video.file_path)
        # Update source status
        db_video.status = SourceStatus.PROCESSING
        db.commit()
        return {'detail': f'Video (id={video_id}) is being streamed.'}

    async def accept_connection(self, source_id: int, websocket: WebSocket):
        await websocket.accept()
        async with self.__connections_lock:
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
            async with self.__connections_lock:
                print('removing socket hell yea!', source_id)
                self.__connections[source_id].remove(websocket)

    async def __stream_to_client(self, db: Session):
        while 1:
            try:
                source_id, enc_frame, success = self.__frames_queue.get(timeout=0.01)
                async with self.__connections_lock:
                    if success and enc_frame is not None:
                        if source_id in self.__connections.keys():
                            for ws in self.__connections[source_id]:
                                await ws.send_bytes(enc_frame.tobytes())
                    else:
                        # Stream ended
                        db_video = self.get_video_by_id(db, source_id)
                        db_video.status = SourceStatus.PROCESSED
                        db.commit()
                        if source_id in self.__connections.keys():
                            for ws in self.__connections[source_id]:
                                await ws.send_json({'source_id': source_id, 'detail': 'Video stream ended!'})
                # Allow other requests to process while streams are running
                await asyncio.sleep(0.01)
            except queue.Empty:
                # Allow other requests to process while no streams are running
                await asyncio.sleep(0.01)
            except BaseException as e:
                e_type, e_object, e_traceback = sys.exc_info()
                print(f'{threading.current_thread().name}\n'
                      f'Error:{e_type}:{e_object}\n{"".join(traceback.format_tb(e_traceback))}')

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
