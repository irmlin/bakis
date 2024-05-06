from datetime import datetime

from pydantic import BaseModel

from ..models.enums import SourceStatus, SourceType


class SourceBase(BaseModel):
    title: str
    description: str
    source_type: SourceType


# TODO: this schema will have analyze_from, analyze_to fields
class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    created_at: datetime
    status: SourceStatus

    class Config:
        orm_mode = True


class SourceReadDetailed(SourceRead):
    num_accidents: int
