from datetime import datetime

from pydantic import BaseModel

from ..models.enums import AccidentType


class AccidentRead(BaseModel):
    id: int
    created_at: datetime
    type: AccidentType

    class Config:
        orm_mode = True
