from datetime import datetime

from pydantic import BaseModel

from ..models.enums import AccidentType


class CarCrashThresholdRead(BaseModel):
    car_crash_threshold: float

    class ConfigDict:
        from_attributes = True


class CarCrashThresholdUpdate(BaseModel):
    car_crash_threshold: float
