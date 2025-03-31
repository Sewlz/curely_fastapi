from pydantic import BaseModel, EmailStr, Field

# Schema cho đăng ký người dùng
class RegisterUserSchema(BaseModel):
    first_name: str = Field(..., title="First Name", description="The user's first name")
    last_name: str = Field(..., title="Last Name", description="The user's last name")
    email: EmailStr = Field(..., title="Email", description="The user's email address")
    phone_number: str = Field(..., title="Phone Number", description="The user's phone number")
    password: str = Field(..., min_length=8, max_length=20, title="Password", description="The user's password")

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