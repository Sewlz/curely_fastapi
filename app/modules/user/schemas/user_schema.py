from datetime import date
from typing import Optional
from app.common.models.base import SecureBaseModel
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.common.validators.validate_input import validate_safe_text, validate_safe_url, validate_dob

class UserBase(BaseModel):
    name: str
    email: EmailStr
    profilePicture: Optional[str] = None
    nickName: Optional[str] = None
    dob: Optional[date] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return validate_safe_text(v)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_safe_text(v)

    @field_validator('nickName')
    @classmethod
    def validate_nickName(cls, v):
        return validate_safe_text(v)

    @field_validator('profilePicture')
    @classmethod
    def validate_profilePicture(cls, v):
        return validate_safe_url(v)

    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v):
        return validate_dob(v)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    profilePicture: Optional[str]
    nickName: Optional[str]
    dob: Optional[date]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return validate_safe_text(v)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_safe_text(v)

    @field_validator('nickName')
    @classmethod
    def validate_nickName(cls, v):
        return validate_safe_text(v)

    @field_validator('profilePicture')
    @classmethod
    def validate_profilePicture(cls, v):
        return validate_safe_url(v)

    @field_validator('dob')
    @classmethod
    def validate_dob(cls, v):
        return validate_dob(v)

class UpdatePasswordSchema(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

    @field_validator('current_password')
    @classmethod
    def validate_current_password(cls, v):
        return validate_safe_text(v)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        return validate_safe_text(v)
