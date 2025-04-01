from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    nickname: Optional[str] = None
    email: EmailStr
    profilePicture: Optional[str] = None
    dob: Optional[date] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    nickname: Optional[str]
    email: Optional[EmailStr]
    profilePicture: Optional[str]
    dob: Optional[date]
