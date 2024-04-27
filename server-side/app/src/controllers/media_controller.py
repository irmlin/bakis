import asyncio
import multiprocessing
import threading

from fastapi import APIRouter, UploadFile, File, Depends, Form, WebSocket, BackgroundTasks
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas import VideoRead, VideoCreate
from ..services import MediaService
from ..socket import WebSocketManager
from ..stream import WorkerStreamReader
import cv2


# TODO: BaseController?
class MediaController:

    def __init__(self):
        self.router = APIRouter(tags=["media"], prefix="/media")
        self.media_service = MediaService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.post("/", response_model=VideoRead)
        def upload_video(title: str = Form(), description: str = Form(), video_file: UploadFile = File(...),
                         db: Session = Depends(get_db)):
            video_create = VideoCreate(title=title, description=description)
            return self.media_service.upload_video(db, video_create, video_file)

        @router.get("/video/stream")
        def get_live_videos(db: Session = Depends(get_db)):
            return self.media_service.get_live_videos(db)

        @router.get("/video/{video_id}")
        def get_video(video_id: int, db: Session = Depends(get_db)):
            return self.media_service.get_video_by_id(db, video_id)

        @router.get("/video")
        def get_all_videos(db: Session = Depends(get_db)):
            return self.media_service.get_all_videos(db)

        @router.delete("/video/{video_id}")
        def delete_video(video_id: int, db: Session = Depends(get_db)):
            return self.media_service.delete_video(db, video_id)

        @router.put("/video/stream/{video_id}")
        async def terminate_live_stream(video_id: int, db: Session = Depends(get_db)):
            print('put endpoint hit', video_id)
            return await self.media_service.terminate_live_stream(db, video_id)

        @router.get("/video/inference/{video_id}")
        async def start_inference(video_id: int, db: Session = Depends(get_db)):
            return await self.media_service.start_inference_task(db, video_id)

        @router.websocket("/video/stream/{video_id}")
        async def stream_video(video_id: int, websocket: WebSocket):
            print(f'socket connecting, source is {video_id}')
            await self.media_service.accept_connection(video_id, websocket)

