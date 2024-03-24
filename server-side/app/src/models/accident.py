from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as EnumType

from .enums import AccidentType
from ..database import Base


class Accident(Base):
    __tablename__ = 'accidents'

    id = Column(Integer, primary_key=True)
    type = Column(EnumType(AccidentType))
    start_ts = Column(Integer)
    end_ts = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow())
    image_path = Column(String(250))
    video_path = Column(String(250))
