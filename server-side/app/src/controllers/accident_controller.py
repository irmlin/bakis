from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_db


class AccidentController:

    def __init__(self):
        self.router = APIRouter(tags=["accident"], prefix="/accident")
        self.accident_service = AccidentService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.get("/video/stream")
        def get_all_accidents(db: Session = Depends(get_db)):
            return self.accident_service.get_all_accidents(db)
