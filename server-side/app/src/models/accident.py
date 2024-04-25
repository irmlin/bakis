from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import relationship

from .enums import AccidentType
from ..database import Base


class Accident(Base):
    __tablename__ = 'accidents'

    id = Column(Integer, primary_key=True)
    type = Column(EnumType(AccidentType))
    created_at = Column(DateTime, default=datetime.utcnow())
    image_path = Column(String(250))
    video_path = Column(String(250))

    video_id = Column(Integer, ForeignKey('videos.id'))  # Foreign key reference to videos.id
    video = relationship("Video", back_populates="accidents")
