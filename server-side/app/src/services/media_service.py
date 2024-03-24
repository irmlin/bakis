import os
import shutil
import uuid

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


class MediaService:

    # TODO add repository class
    def __init__(self):
        self.file_size_limit_bytes = FileSize.GB
        self.socket_manager = WebSocketManager()

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
        self.__delete_video_file(db_video.file_path)
        db.delete(db_video)
        db.commit()
        return {'detail': f'Video (id={video_id}) has been deleted.'}

    async def start_inference_task(self, db: Session, video_id: int, background_tasks: BackgroundTasks):
        db_video = self.get_video_by_id(db, video_id)
        if db_video is None:
            raise HTTPException(status_code=404, detail=f'Video with id {video_id} not found')
        if not self.__video_file_exists(db_video.file_path):
            raise HTTPException(status_code=404, detail=f'Video (id={video_id}) file not found')
        # background_tasks.add_task(self.socket_manager.add_stream, video_id, db_video.file_path)
        await self.socket_manager.add_stream(video_id, db_video.file_path)
        return {'detail': f'Video (id={video_id}) is being streamed.'}

    async def stream_video(self, video_id: int, websocket: WebSocket):
        await self.socket_manager.subscribe(video_id, websocket)

        try:
            while True:
                # The websocket will be destroyed if this method terminates.
                # We can check for any incoming messages, while in the background
                # data is continuously sent to clients.
                await websocket.receive_text()
        except WebSocketDisconnect as e:
            await self.socket_manager.unsubscribe(video_id, websocket)

    @staticmethod
    def get_file_size(file: UploadFile) -> int:
        _ = file.file.seek(0, 2)
        file_size_bytes = file.file.tell()
        file.file.seek(0)
        return file_size_bytes

    def get_video_by_id(self, db: Session, video_id: int):
        return db.query(Video).filter(Video.id == video_id).first()

    def get_videos(self, db: Session):
        return db.query(Video).all()

    def __video_file_exists(self, file_path: str):
        return os.path.exists(file_path)

    def __delete_video_file(self, file_path: str):
        if self.__video_file_exists(file_path):
            os.remove(file_path)
