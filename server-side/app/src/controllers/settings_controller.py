from typing import List, Optional

from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form
from typing_extensions import Annotated

from ..dependencies import get_db, get_current_user
from ..schemas import CarCrashThresholdRead, CarCrashThresholdUpdate, RecipientRead
from ..services import SettingsService


class SettingsController:

    def __init__(self):
        self.router = APIRouter(tags=["settings"], prefix="/settings")
        self.settings_service = SettingsService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.get("/threshold", response_model=CarCrashThresholdRead)
        def get_threshold(db: Session = Depends(get_db)):
            return self.settings_service.get_threshold(db=db)

        @router.put("/threshold", response_model=CarCrashThresholdUpdate)
        def update_threshold(current_user: Annotated[str, Depends(get_current_user)], threshold: float = Form(), db: Session = Depends(get_db)):
            return self.settings_service.update_threshold(db=db, new_thr=threshold)

        @router.get("/recipient", response_model=List[RecipientRead])
        def get_recipients(current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
            return self.settings_service.get_recipients(db=db)

        @router.post("/recipient", response_model=RecipientRead)
        def add_recipient(current_user: Annotated[str, Depends(get_current_user)], email: Optional[str] = Form(None), db: Session = Depends(get_db)):
            return self.settings_service.add_recipient(db=db, email=email)

        @router.delete("/recipient/{recipient_id}")
        def delete_recipient(current_user: Annotated[str, Depends(get_current_user)], recipient_id: int, db: Session = Depends(get_db)):
            return self.settings_service.delete_recipient(db=db, recipient_id=recipient_id)
