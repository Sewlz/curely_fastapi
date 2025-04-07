from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    email: EmailStr
    profilePicture: Optional[str] = None
    nickName: Optional[str] = None
    dob: Optional[date] = None  # Ngày sinh

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    profilePicture: Optional[str]
    nickName: Optional[str]
    dob: Optional[date]


