"""
Схемы для текстов.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserTextInput(BaseModel):
    """Входные данные для создания текста."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Содержание текста (макс. 10000 символов)"
    )
    language: Optional[str] = Field("zh", description="Код языка (zh, en, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "我喜欢学习中文。今天天气很好。",
                "language": "zh",
            }
        }


class UserTextOutput(BaseModel):
    """Результат создания/получения текста."""
    id: int
    content: str
    language: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Данные токена."""
    value: str
    lemma: Optional[str] = None
    frequency: int = 1
    position: Optional[int] = None
    is_known: bool = False
    hsk: Optional[int] = None


class TextAnalyzeResponse(BaseModel):
    """Результат анализа текста."""
    status: str
    text_id: int
    content: Optional[str] = None
    tokens_count: int = 0
    tokens_created: Optional[int] = None
    tokens: Optional[List[TokenData]] = None

    class Config:
        from_attributes = True


class WordReplacement(BaseModel):
    """Замена слова при упрощении."""
    original: str
    replacement: str
    reason: str
    hsk_level: int
    similarity: float


class SimplifyRequest(BaseModel):
    """Запрос на упрощение текста (для endpoint с text_id)."""
    target_level: int = Field(..., ge=1, le=6, description="Целевой уровень HSK (1-6)")

    class Config:
        json_schema_extra = {
            "example": {
                "target_level": 2,
            }
        }


class SimplifyRequestDirect(BaseModel):
    """Запрос на упрощение текста (прямой, без сохранения в БД)."""
    text: str
    target_level: int = Field(..., ge=1, le=6, description="Целевой уровень HSK (1-6)")
    language: Optional[str] = Field("zh", description="Код языка")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "我喜欢学习中文。今天天气很好。",
                "target_level": 2,
                "language": "zh",
            }
        }


class SimplifyResponse(BaseModel):
    """Результат упрощения текста."""
    status: str
    original_text: str
    simplified_text: str
    replacements: Optional[List[WordReplacement]] = None
    target_level: int
    total_tokens: int
    replaced_count: int

    class Config:
        from_attributes = True
