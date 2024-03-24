from enum import Enum


class AccidentType(str, Enum):
    CAR_CRASH = "CAR_CRASH"
    FIRE = "FIRE"
    VIOLENCE = "VIOLENCE"
