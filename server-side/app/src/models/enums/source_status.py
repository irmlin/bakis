from enum import Enum


class SourceStatus(str, Enum):
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    NOT_PROCESSED = "NOT_PROCESSED"
    TERMINATED = "TERMINATED"
