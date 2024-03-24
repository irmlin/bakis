from datetime import datetime

from pydantic import BaseModel

from ..models.enums import SourceStatus


class VideoBase(BaseModel):
    title: str
    description: str


# TODO: this schema will have analyze_from, analyze_to fields
class VideoCreate(VideoBase):
    pass


class VideoRead(VideoBase):
    id: int
    created_at: datetime
    status: SourceStatus

    class Config:
        orm_mode = True
