# Module: app.schemas.user
# Description: Pydantic validation schemas defining auth requests, logins payloads, and user details returns.

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID


class UserBaseSchema(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "analyst"


class UserRegisterSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, description="Strong passwords constraint")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        import re
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")
        return value


class UserResponseSchema(UserBaseSchema):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProfileUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str | None) -> str | None:
        if value is None:
            return value
        import re
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character.")
        return value

