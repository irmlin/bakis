from fastapi import HTTPException
from pydantic_core._pydantic_core import ValidationError
from sqlalchemy.orm import Session

from ..models import Threshold, Recipient
from ..models.validation_models import ThresholdRangeValidator, EmailValidator
# from ..utilities import ThresholdSingleton


class SettingsService:

    def __init__(self):
        pass

    def get_threshold(self, db: Session):
        threshold = db.query(Threshold).first()
        return threshold

    def update_threshold(self, db: Session, new_thr: float):
        try:
            ThresholdRangeValidator(threshold=new_thr)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f'Threshold must be in range [0.0; 1.0]!')
        db_threshold = self.get_threshold(db)
        if db_threshold is None:
            raise HTTPException(status_code=404, detail=f'Server could not find threshold setting!')
        db_threshold.car_crash_threshold = new_thr
        db.commit()
        # ThresholdSingleton().set(value=new_thr)

        return db_threshold

    def get_recipients(self, db: Session):
        return db.query(Recipient).all()

    def get_recipient_by_id(self, db: Session, recipient_id: int):
        return db.query(Recipient).filter(Recipient.id == recipient_id).first()

    def __get_recipient_by_email(self, db: Session, email: str):
        return db.query(Recipient).filter(Recipient.email == email).first()

    def add_recipient(self, db: Session, email: str):
        try:
            EmailValidator(email=email)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f'Invalid email format provided!')
        duplicate = self.__get_recipient_by_email(db=db, email=email)
        if duplicate is not None:
            raise HTTPException(status_code=400, detail='Email already exists!')
        r_new = Recipient(email=email)
        db.add(r_new)
        db.commit()
        return r_new

    def delete_recipient(self, db: Session, recipient_id: int):
        db_recipient = self.get_recipient_by_id(db=db, recipient_id=recipient_id)
        if db_recipient is None:
            raise HTTPException(status_code=404, detail=f'Recipient with id {recipient_id} does not exist!')
        db.delete(db_recipient)
        db.commit()
        return {'detail': f'Recipient with id {recipient_id} deleted successfully!'}
