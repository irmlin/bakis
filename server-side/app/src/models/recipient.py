from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import relationship

from .enums import AccidentType
from ..database import Base


class Recipient(Base):
    __tablename__ = 'recipients'

    id = Column(Integer, primary_key=True)
    email = Column(String(250))
