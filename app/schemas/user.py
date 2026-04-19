from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    is_banned: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    permissions: List[str]
    ban_reason: Optional[str]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: str
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class UserBanRequest(BaseModel):
    is_banned: bool
    ban_reason: Optional[str] = None


class PermissionRequest(BaseModel):
    permission: str
