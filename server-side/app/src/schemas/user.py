from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    username: str

    class ConfigDict:
        from_attributes = True
