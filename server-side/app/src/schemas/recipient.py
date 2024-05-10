from datetime import datetime

from pydantic import BaseModel


class BaseRecipient(BaseModel):
    email: str


class RecipientRead(BaseRecipient):
    id: int
    class ConfigDict:
        from_attributes = True
