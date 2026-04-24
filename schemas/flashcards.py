"""
Схемы для карточек и повторений.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FlashcardCreate(BaseModel):
    """Данные для создания карточки."""
    word: str = Field(..., min_length=1, max_length=200, description="Слово")
    context: Optional[str] = Field(None, description="Контекст (пример из текста)")
    translation: Optional[str] = Field(None, max_length=1000, description="Перевод")

    class Config:
        json_schema_extra = {
            "example": {
                "word": "学习",
                "context": "我喜欢学习中文。",
                "translation": "учить, изучать",
            }
        }


class FlashcardResponse(BaseModel):
    """Информация о карточке."""
    id: int
    user_id: int
    word: str
    context: Optional[str] = None
    translation: Optional[str] = None
    easiness_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FlashcardList(BaseModel):
    """Список карточек с пагинацией."""
    items: List[FlashcardResponse]
    total: int
    page: int
    size: int


class GenerateFlashcardsRequest(BaseModel):
    """Запрос на генерацию карточек из текста."""
    text_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "text_id": 1,
            }
        }


class GenerateFlashcardsResponse(BaseModel):
    """Результат генерации карточек."""
    status: str
    text_id: int
    cards_created: int
    cards_skipped: int
    flashcards: Optional[List[FlashcardResponse]] = None


class ReviewCreate(BaseModel):
    """Оценка повторения карточки (0-5)."""
    quality: int = Field(..., ge=0, le=5, description="Качество ответа (0-5)")

    class Config:
        json_schema_extra = {
            "example": {
                "quality": 4,
            }
        }


class ReviewResponse(BaseModel):
    """Информация о повторении."""
    id: int
    flashcard_id: int
    quality: int
    reviewed_at: datetime

    class Config:
        from_attributes = True
