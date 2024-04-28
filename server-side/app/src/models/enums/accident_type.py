from enum import Enum


class AccidentType(str, Enum):
    CAR_CRASH = "CAR_CRASH"
    FIRE = "FIRE"
    VIOLENCE = "VIOLENCE"


accident_type_str_map = {
    AccidentType.CAR_CRASH: 'Car Crash',
    AccidentType.FIRE: 'Fire',
    AccidentType.VIOLENCE: 'Violence'
}