from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Depends, Form, WebSocket
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from ..dependencies import get_db, get_current_user
from ..schemas import SourceRead, SourceCreate, SourceReadDetailed
from ..services import SourceService

from ..models.enums import SourceType


class SourceController:

    def __init__(self):
        self.router = APIRouter(tags=["media"], prefix="/media")
        self.source_service = SourceService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.post("/", response_model=SourceRead)
        def upload_source(current_user: Annotated[str, Depends(get_current_user)], title: str = Form(), description: str = Form(), video_file: UploadFile = File(None),
                          source_type: SourceType = Form(), stream_url: Optional[str] = Form(None),
                          db: Session = Depends(get_db)):
            source_create = SourceCreate(title=title, description=description, source_type=source_type)
            return self.source_service.upload_source(db, source_create, video_file, stream_url)

        @router.get("/source/stream")
        def get_live_sources(db: Session = Depends(get_db)):
            return self.source_service.get_live_sources(db)

        @router.get("/source/{source_id}")
        def get_source(source_id: int, db: Session = Depends(get_db)):
            return self.source_service.get_source_by_id(db, source_id)

        @router.get("/source", response_model=List[SourceReadDetailed])
        def get_all_sources(db: Session = Depends(get_db), skip: int = None, limit: int = None):
            return self.source_service.get_all_sources(db, skip, limit)

        @router.delete("/source/{source_id}")
        def delete_source(current_user: Annotated[str, Depends(get_current_user)], source_id: int, db: Session = Depends(get_db)):
            return self.source_service.delete_source(db, source_id)

        @router.put("/source/stream/{source_id}")
        async def terminate_live_stream(current_user: Annotated[str, Depends(get_current_user)], source_id: int, db: Session = Depends(get_db)):
            print('put endpoint hit', source_id)
            return await self.source_service.terminate_live_stream(db, source_id)

        @router.get("/source/inference/{source_id}")
        async def start_inference(current_user: Annotated[str, Depends(get_current_user)], source_id: int, db: Session = Depends(get_db)):
            return await self.source_service.start_inference_task(db, source_id)

        @router.websocket("/source/stream/{source_id}")
        async def stream_source(source_id: int, websocket: WebSocket):
            print(f'socket connecting, source is {source_id}')
            await self.source_service.accept_connection(source_id, websocket)

