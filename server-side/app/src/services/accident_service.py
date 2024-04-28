import base64
import os
from typing import Tuple

from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.responses import FileResponse
import cv2

from ..models import Accident


class AccidentService:

    def __init__(self):
        pass

    def get_accident_by_id(self, db: Session, accident_id: int):
        return db.query(Accident).filter(Accident.id == accident_id).first()

    def get_all_accidents(self, db: Session):
        return db.query(Accident).all()

    def get_accident_image(self, accident_id: int, db: Session):
        db_accident = self.get_accident_by_id(db, accident_id)
        if db_accident is None:
            raise HTTPException(status_code=404, detail=f'Accident with id {accident_id} not found.')
        if not self.__file_exists(db_accident.image_path):
            raise HTTPException(status_code=404, detail=f'No image found for accident with id {accident_id}.')

        with open(db_accident.image_path, 'rb') as f:
            base64image = base64.b64encode(f.read())
        return base64image

    def get_accident_video(self, accident_id: int, db: Session) -> Tuple[str, str]:
        db_accident: Accident = self.get_accident_by_id(db, accident_id)
        if db_accident is None:
            raise HTTPException(status_code=404, detail=f'Accident with id {accident_id} not found.')
        if not self.__file_exists(db_accident.video_path):
            raise HTTPException(status_code=404, detail=f'No video found for accident with id {accident_id}.')

        ext = os.path.splitext(db_accident.video_path)[1]
        return (db_accident.video_path,
                f'{db_accident.created_at}_from_{db_accident.video.title}_type_{db_accident.type}{ext}')

    # TODO: move to utils
    def __file_exists(self, file_path: str):
        return os.path.exists(file_path)

    def __delete_file(self, file_path: str):
        if self.__file_exists(file_path):
            os.remove(file_path)
