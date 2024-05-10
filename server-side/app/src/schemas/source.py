from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.enums import SourceStatus, SourceType


class SourceBase(BaseModel):
    title: str
    description: str
    source_type: SourceType
    stream_url: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    created_at: datetime
    status: SourceStatus

    class ConfigDict:
        from_attributes = True


class SourceReadDetailed(SourceRead):
    num_accidents: int
