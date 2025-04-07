
from pydantic import BaseModel, EmailStr, Field
# Schema cho đăng nhập người dùng
class LoginSchema(BaseModel):
    email: EmailStr = Field(..., title="Email", description="The user's email address")
    password: str = Field(..., min_length=8, max_length=20, title="Password", description="The user's password")