from pydantic import BaseModel, EmailStr ,Field
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    profilePicture: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    profilePicture: Optional[str]

# Schema cho thay đổi mật khẩu
class ChangePasswordSchema(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=20, title="Old Password", description="The user's current password")
    new_password: str = Field(..., min_length=8, max_length=20, title="New Password", description="The new password for the user")
    confirm_password: str = Field(..., min_length=8, max_length=20, title="Confirm Password", description="Confirm the new password")