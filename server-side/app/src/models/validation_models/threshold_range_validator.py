from pydantic import BaseModel, field_validator, ValidationInfo


class ThresholdRangeValidator(BaseModel):
    threshold: float

    @field_validator('threshold')
    @classmethod
    def validate_threshold(cls, value: float, info: ValidationInfo):
        if value < 0.0 or value > 1.0:
            raise ValueError('Threshold value must be between 0.0 and 1.0')
        return value