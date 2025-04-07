from pydantic import BaseModel, EmailStr, Field

class RegisterUserSchema(BaseModel):
    name: str = Field(..., title="Full Name", description="The user's full name")
    email: EmailStr = Field(..., title="Email", description="The user's email address")
    password: str = Field(..., min_length=8, max_length=20, title="Password", description="The user's password")
    confirm_password: str = Field(..., min_length=8, max_length=20, title="Confirm Password", description="Must match the user's password")

# Schema cho đăng nhập người dùng
class LoginSchema(BaseModel):
    email: EmailStr = Field(..., title="Email", description="The user's email address")
    password: str = Field(..., min_length=8, max_length=20, title="Password", description="The user's password")

# Schema cho quên mật khẩu
class ForgotPasswordSchema(BaseModel):
    email: EmailStr = Field(..., title="Email", description="The user's email address for password reset")

# Schema cho đăng nhập bằng Google
class GoogleLoginSchema(BaseModel):
    id_token: str

class FacebookLoginSchema(BaseModel):
    id_token: str

