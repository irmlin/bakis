from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as EnumType

from .enums import SourceStatus
from ..database import Base


#TODO: add analyze_from, analyze_to columns (time)
class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(250))
    file_path = Column(String(250))
    created_at = Column(DateTime, default=datetime.utcnow())
    status = Column(EnumType(SourceStatus), default=SourceStatus.NOT_PROCESSED)