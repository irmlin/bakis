from sqlalchemy import Column, Integer, Float

from ..database import Base


class Setting(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    created_at = Column(Float)
