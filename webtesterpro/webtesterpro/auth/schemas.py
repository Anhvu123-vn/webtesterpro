"""
Pydantic schemas cho Authentication API.

Tách biệt khỏi SQLAlchemy models để validate input/output an toàn.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Thông tin cơ bản của user."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema đăng ký tài khoản mới."""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """Username chỉ chứa chữ, số và dấu gạch dưới."""
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username chỉ được chứa chữ cái, số và dấu gạch dưới")
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Yêu cầu mật khẩu có ít nhất 1 chữ hoa, 1 chữ thường và 1 số."""
        if not re.search(r"[A-Z]", value):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa")
        if not re.search(r"[a-z]", value):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ thường")
        if not re.search(r"\d", value):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ số")
        return value


class UserLogin(BaseModel):
    """Schema đăng nhập — dùng email hoặc username."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    """Schema trả về thông tin user (không bao gồm password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """Response chứa JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload bên trong JWT."""

    sub: str  # user id dạng string
    type: str = "access"  # "access" hoặc "refresh"
    exp: Optional[int] = None


class MessageResponse(BaseModel):
    """Response thông báo đơn giản."""

    message: str


class ReportCreate(BaseModel):
    """Schema tạo report mới."""

    title: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=2048)
    file_path: Optional[str] = None
    json_path: Optional[str] = None
    overall_score: Optional[int] = Field(None, ge=0, le=100)
    summary: Optional[str] = None


class ReportResponse(ReportCreate):
    """Schema trả về report."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str = "completed"
    created_at: datetime
