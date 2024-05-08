from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Depends, Form, WebSocket
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas import SourceRead, SourceCreate, SourceReadDetailed
from ..services import MediaService

from ..models.enums import SourceType


# TODO: BaseController?
class MediaController:

    def __init__(self):
        self.router = APIRouter(tags=["media"], prefix="/media")
        self.media_service = MediaService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.post("/", response_model=SourceRead)
        def upload_source(title: str = Form(), description: str = Form(), video_file: UploadFile = File(None),
                          source_type: SourceType = Form(), stream_url: Optional[str] = Form(None),
                          db: Session = Depends(get_db)):
            source_create = SourceCreate(title=title, description=description, source_type=source_type)
            return self.media_service.upload_source(db, source_create, video_file, stream_url)

        @router.get("/source/stream")
        def get_live_sources(db: Session = Depends(get_db)):
            return self.media_service.get_live_sources(db)

        @router.get("/source/{source_id}")
        def get_source(source_id: int, db: Session = Depends(get_db)):
            return self.media_service.get_source_by_id(db, source_id)

        @router.get("/source", response_model=List[SourceReadDetailed])
        def get_all_sources(db: Session = Depends(get_db), skip: int = None, limit: int = None):
            return self.media_service.get_all_sources(db, skip, limit)

        @router.delete("/source/{source_id}")
        def delete_source(source_id: int, db: Session = Depends(get_db)):
            return self.media_service.delete_source(db, source_id)

        @router.put("/source/stream/{source_id}")
        async def terminate_live_stream(source_id: int, db: Session = Depends(get_db)):
            print('put endpoint hit', source_id)
            return await self.media_service.terminate_live_stream(db, source_id)

        @router.get("/source/inference/{source_id}")
        async def start_inference(source_id: int, db: Session = Depends(get_db)):
            return await self.media_service.start_inference_task(db, source_id)

        @router.websocket("/source/stream/{source_id}")
        async def stream_source(source_id: int, websocket: WebSocket):
            print(f'socket connecting, source is {source_id}')
            await self.media_service.accept_connection(source_id, websocket)

