from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime


class DateRangeParams(BaseModel):
    datetime_from: Optional[datetime] = None
    datetime_to: Optional[datetime] = None
