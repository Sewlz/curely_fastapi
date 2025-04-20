from typing import Optional
from datetime import datetime
from pydantic import field_validator
from app.common.models.base import SecureBaseModel
from app.common.validators.validate_input import validate_safe_text, validate_uuid

class InputData(SecureBaseModel):
    session_id: str
    prompt: str

    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        return validate_uuid(v)

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        return validate_safe_text(v)

class OutputData(SecureBaseModel):
    response: str

    @field_validator('response')
    @classmethod
    def validate_response(cls, v):
        return validate_safe_text(v)

class ChatMessageSchema(SecureBaseModel):
    session_id: str
    user_id: str
    sender: str
    message: str
    timestamp: Optional[datetime] = None

    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        return validate_uuid(v)

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        return validate_uuid(v)

    @field_validator('sender')
    @classmethod
    def validate_sender(cls, v):
        return validate_safe_text(v)

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        return validate_safe_text(v)

class ChatSessionCreate(SecureBaseModel):
    session_name: str

    @field_validator('session_name')
    @classmethod
    def validate_session_name(cls, v):
        return validate_safe_text(v)

class ChatSession(SecureBaseModel):
    session_id: str
    user_id: str
    session_name: str
    status: str
    created_at: Optional[datetime]

    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        return validate_uuid(v)

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        return validate_uuid(v)

    @field_validator('session_name')
    @classmethod
    def validate_session_name(cls, v):
        return validate_safe_text(v)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        return validate_safe_text(v)
