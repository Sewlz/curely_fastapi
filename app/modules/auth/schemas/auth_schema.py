from app.common.models.base import SecureBaseModel
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.common.validators.validate_input import validate_safe_text

class RegisterUserSchema(SecureBaseModel):
    name: str = Field(..., title="Full Name", description="The user's full name")
    email: EmailStr = Field(..., title="Email", description="The user's email address")
    password: str = Field(..., min_length=8, max_length=20, title="Password", description="The user's password")
    confirm_password: str = Field(..., min_length=8, max_length=20, title="Confirm Password", description="Must match the user's password")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_safe_text(v)

    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v):
        return validate_safe_text(v)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_safe_text(v)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return validate_safe_text(v)

class LoginSchema(SecureBaseModel):
    email: EmailStr = Field(..., title="Email", description="The user's email address")
    password: str = Field(..., min_length=8, max_length=20, title="Password", description="The user's password")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_safe_text(v)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_safe_text(v)

class ForgotPasswordSchema(SecureBaseModel):
    email: EmailStr = Field(..., title="Email", description="The user's email address for password reset")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return validate_safe_text(v)

class GoogleLoginSchema(SecureBaseModel):
    id_token: str

class FacebookLoginSchema(SecureBaseModel):
    id_token: str

