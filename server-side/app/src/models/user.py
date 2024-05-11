from sqlalchemy import Column, Integer, String, DateTime, func

from ..database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    password_hash = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())