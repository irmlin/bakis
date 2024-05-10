from typing import List, Union

from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class UserUpdate(BaseModel):
    email: str
    password: str
