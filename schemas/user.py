"""
Схемы для пользователей.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Данные для регистрации."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    lang_level: Optional[str] = Field(None, description="Уровень языка (например, HSK 1-6)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "user123",
                "password": "password123",
                "lang_level": "HSK 2",
            }
        }


class UserLogin(BaseModel):
    """Данные для входа."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
            }
        }


class UserResponse(BaseModel):
    """Информация о пользователе."""
    id: int
    email: EmailStr
    username: str
    lang_level: Optional[str] = None
    created_at: datetime
    token: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Данные для обновления профиля."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=50)
    lang_level: Optional[str] = None
    is_active: Optional[bool] = None
