from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..services import AccidentService
from ..schemas import AccidentRead


class AccidentController:

    def __init__(self):
        self.router = APIRouter(tags=["accident"], prefix="/accident")
        self.accident_service = AccidentService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.get("", response_model=List[AccidentRead])
        def get_all_accidents(db: Session = Depends(get_db)):
            return self.accident_service.get_all_accidents(db)

        @router.get("/image/{accident_id}")
        def get_accident_image(accident_id: int, db: Session = Depends(get_db)):
            data = self.accident_service.get_accident_image(accident_id, db)
            return Response(content=data, media_type="image/jpeg")
