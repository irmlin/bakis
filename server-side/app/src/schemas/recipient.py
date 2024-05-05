from datetime import datetime

from pydantic import BaseModel


class BaseRecipient(BaseModel):
    email: str


class RecipientRead(BaseRecipient):
    id: int
    class Config:
        orm_mode = True
