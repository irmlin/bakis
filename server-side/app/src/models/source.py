from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import relationship

from .enums import SourceStatus, SourceType
from ..database import Base


#TODO: add analyze_from, analyze_to columns (time)
class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(250))
    file_path = Column(String(250))
    created_at = Column(DateTime)
    status = Column(EnumType(SourceStatus), default=SourceStatus.NOT_PROCESSED)
    fps = Column(Float)
    height = Column(Float)
    width = Column(Float)
    source_type = Column(EnumType(SourceType), default=SourceType.VIDEO)
    stream_url = Column(String(250))

    accidents = relationship("Accident", back_populates="source")
