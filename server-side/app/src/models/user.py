from typing import List, Optional
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base

from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email = Column(String(50))
    password_hash = Column(String(100))
    created_at = Column(DateTime)
    is_active = Column(Boolean, default=False)
