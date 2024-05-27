from pydantic import BaseModel, field_validator, ValidationInfo, EmailStr


class EmailValidator(BaseModel):
    email: EmailStr
