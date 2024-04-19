import asyncio
import multiprocessing
import os
import queue
import shutil
import uuid
from multiprocessing import Queue
from typing import List, Dict

import cv2
import numpy as np
from fastapi import UploadFile, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models import Video
from ..schemas import VideoCreate
from ..socket import WebSocketManager
from ..utilities.file_size import FileSize
from ..models.enums import SourceStatus
from ..stream import WorkerStreamReader


class MediaService:

    # TODO add repository class
    def __init__(self):
        self.file_size_limit_bytes = FileSize.GB
        self.socket_manager = WebSocketManager()

        # Data traffic from processing job to this
        self.__connections: Dict[int, List[WebSocket]] = {}
        self.__connections_lock: asyncio.Lock = asyncio.Lock()
        self.__frames_queue = Queue(maxsize=500)

        # Data traffic from current process to processing job
        self.__manager = multiprocessing.Manager()
        self.__shared_sources_dict = self.__manager.dict()
        self.__shared_connections_dict = self.__manager.dict()
        self.__worker_stream_reader = WorkerStreamReader(shared_sources_dict=self.__shared_sources_dict,
                                                         shared_connections_dict=self.__shared_connections_dict,
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
        print('video_uploaded')
        return video

    def delete_video(self, db: Session, video_id: int):
        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found.')
        self.__delete_video_file(db_video.file_path)
        db.delete(db_video)
        db.commit()
        return {'detail': f'Video (id={video_id}) has been deleted.'}

    def start_inference_task(self, db: Session, video_id: int, background_tasks: BackgroundTasks):
        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found')
        if not self.__video_file_exists(db_video.file_path):
            raise HTTPException(status_code=404, detail=f'Video (id={video_id}) file not found')
        # background_tasks.add_task(self.socket_manager.add_stream, video_id, db_video.file_path)
        # # await self.socket_manager.add_stream(video_id, db_video.file_path)

        print('trying to start inference')
        self.__worker_stream_reader.add_source(video_id, db_video.file_path)
        # Update source status
        db_video.status = SourceStatus.PROCESSING
        db.commit()
        print('this endpoint finished')
        return {'detail': f'Video (id={video_id}) is being streamed.'}

    async def accept_connection(self, video_id: int, websocket: WebSocket):
        await websocket.accept()
        print('accepted websocket')
        async with self.__connections_lock:
            if video_id in self.__connections.keys():
                print('appending websocket')
                self.__connections[video_id].append(websocket)
            else:
                print('adding new websocket')
                self.__connections[video_id] = [websocket]
        print('after', self.__connections)

        try:
            while True:
                # The websocket will be destroyed if this method terminates.
                # We can check for any incoming messages, while in the background
                # data is continuously sent to clients.
                await websocket.receive_text()
        except WebSocketDisconnect as e:
            with self.__connections_lock:
                self.__connections[video_id].remove(websocket)

    async def stream_to_client(self, db: Session):
        while 1:
            try:
                print('reading queue')
                source_id, enc_frame = self.__frames_queue.get(timeout=1)
                print('found stuff for ', source_id, 'connections:', self.__connections)
                async with self.__connections_lock:
                    for ws in self.__connections[source_id]:
                        await ws.send_text(enc_frame.tobytes())
            except queue.Empty:
                continue
            except BaseException as e:
                print('fuck')
                print(e)

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
