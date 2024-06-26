from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import relationship

from .enums import AccidentType
from ..database import Base


class Accident(Base):
    __tablename__ = 'accidents'

    id = Column(Integer, primary_key=True)
    type = Column(EnumType(AccidentType))
    created_at = Column(DateTime)
    image_path = Column(String(250))
    video_path = Column(String(250))
    score = Column(Float)

    source_id = Column(Integer, ForeignKey('sources.id'))  # Foreign key reference to sources.id
    source = relationship("Source", back_populates="accidents")
