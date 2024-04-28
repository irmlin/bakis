from datetime import datetime

from pydantic import BaseModel

from ..models.enums import AccidentType
from ..schemas import VideoBase


class AccidentRead(BaseModel):
    id: int
    created_at: datetime
    type: AccidentType
    score: float
    video_id: int
    video: VideoBase

    class Config:
        orm_mode = True
