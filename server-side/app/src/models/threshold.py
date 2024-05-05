from sqlalchemy import Column, Integer, Float

from ..database import Base


class Threshold(Base):
    __tablename__ = 'thresholds'

    id = Column(Integer, primary_key=True)
    car_crash_threshold = Column(Float, default=0.8)
