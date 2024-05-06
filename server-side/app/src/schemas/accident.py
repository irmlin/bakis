from datetime import datetime

from pydantic import BaseModel

from ..models.enums import AccidentType
from ..schemas import SourceBase


class AccidentRead(BaseModel):
    id: int
    created_at: datetime
    type: AccidentType
    score: float
    source_id: int
    source: SourceBase

    class Config:
        orm_mode = True
