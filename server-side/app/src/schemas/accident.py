from datetime import datetime

from pydantic import BaseModel

from ..models.enums import AccidentType
from ..schemas import SourceBase


class AccidentBase(BaseModel):
    type: AccidentType
    score: float
    source_id: int
    created_at: datetime


class AccidentRead(AccidentBase):
    id: int
    source: SourceBase

    class ConfigDict:
        from_attributes = True


class AccidentCreate(AccidentBase):
    image_path: str
    video_path: str
