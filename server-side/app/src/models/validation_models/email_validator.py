from pydantic import BaseModel, field_validator, ValidationInfo, EmailStr


class EmailValidator(BaseModel):
    email: EmailStr

    # @field_validator('email')
    # @classmethod
    # def validate_threshold(cls, value: str, info: ValidationInfo):
    #     if value < 0.0 or value > 1.0:
    #         raise ValueError(f'Invalid email format provided: {value}.')
    #     return value
