from typing import Optional
from pydantic import field_validator
from app.common.models.base import SecureBaseModel
from app.common.validators.validate_input import validate_uuid, validate_safe_text, validate_safe_url

class PredictionResult(SecureBaseModel):
    message: str
    aiPrediction: str
    confidenceScore: float

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        return validate_safe_text(v)

    @field_validator('aiPrediction')
    @classmethod
    def validate_prediction(cls, v):
        return validate_safe_text(v)

class DiagnosisRecord(SecureBaseModel):
    diagnosisId: str
    typeId: str
    historyId: str
    mriImageUrl: str
    aiPrediction: str
    confidenceScore: float
    diagnosedAt: Optional[str] = None

    @field_validator('diagnosisId')
    @classmethod
    def validate_diagnosis_id(cls, v):
        return validate_uuid(v)

    @field_validator('typeId')
    @classmethod
    def validate_type_id(cls, v):
        return validate_uuid(v)

    @field_validator('historyId')
    @classmethod
    def validate_history_id(cls, v):
        return validate_uuid(v)

    @field_validator('mriImageUrl')
    @classmethod
    def validate_image_url(cls, v):
        return validate_safe_url(v)

    @field_validator('aiPrediction')
    @classmethod
    def validate_ai_prediction(cls, v):
        return validate_safe_text(v)

    @field_validator('diagnosedAt')
    @classmethod
    def validate_diagnosedAt(cls, v):
        return validate_safe_text(v)