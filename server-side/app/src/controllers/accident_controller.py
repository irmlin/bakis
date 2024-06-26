from typing import List

from fastapi import APIRouter, Depends, Response, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from ..dependencies import get_db, get_current_user
from ..services import AccidentService
from ..schemas import AccidentRead
from ..models.validation_models import DateRangeParams


class AccidentController:

    def __init__(self):
        self.router = APIRouter(tags=["accident"], prefix="/accident")
        self.accident_service = AccidentService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.get("", response_model=List[AccidentRead])
        def get_accidents(db: Session = Depends(get_db), skip: int = 0, limit: int = 10,
                          datetime_from: str = None, datetime_to: str = None,
                          source_ids: List[int] = Query(None)):
            return self.accident_service.get_filtered_accidents(db=db, skip=skip, limit=limit,
                                                                datetime_from=datetime_from,
                                                                datetime_to=datetime_to,
                                                                source_ids=source_ids)

        @router.get("/image/{accident_id}")
        def get_accident_image(accident_id: int, db: Session = Depends(get_db)):
            data = self.accident_service.get_accident_image(accident_id, db)
            return Response(content=data, media_type="image/jpeg")

        @router.get("/video/download/{accident_id}")
        def download_accident_video(accident_id: int, db: Session = Depends(get_db)):
            video_path, video_name = self.accident_service.download_accident_video(accident_id, db)
            return FileResponse(path=video_path, filename=video_name, media_type="video/mp4",
                                headers={'Access-Control-Expose-Headers': 'Content-Disposition'})

        @router.get("/report/pdf")
        def download_report_pdf(datetime_from: str = None, datetime_to: str = None,
                                source_ids: List[int] = Query(None), db: Session = Depends(get_db)):
            pdf_path, pdf_name = self.accident_service.download_report_pdf(db=db, datetime_from=datetime_from,
                                                                           datetime_to=datetime_to,
                                                                           source_ids=source_ids)
            return FileResponse(path=pdf_path, filename=pdf_name, media_type="application/pdf",
                                headers={'Access-Control-Expose-Headers': 'Content-Disposition'})

        @router.get("/report/excel")
        def download_report_excel(datetime_from: str = None, datetime_to: str = None,
                                  source_ids: List[int] = Query(None), db: Session = Depends(get_db)):
            excel_path, excel_name = self.accident_service.download_report_excel(db=db, datetime_from=datetime_from,
                                                                                 datetime_to=datetime_to,
                                                                                 source_ids=source_ids)
            return FileResponse(path=excel_path, filename=excel_name,
                                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                headers={'Access-Control-Expose-Headers': 'Content-Disposition'})

        @router.delete("/{accident_id}")
        def delete_accident(current_user: Annotated[str, Depends(get_current_user)], accident_id: int, db: Session = Depends(get_db)):
            return self.accident_service.delete_accident(db, accident_id)