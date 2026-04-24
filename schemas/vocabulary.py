"""
Схемы для словаря пользователя.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class VocabularyStatus(str, Enum):
    """Статус слова в словаре."""
    KNOW = "known"
    LEARNING = "learning"
    IGNORED = "ignored"


class VocabularyBase(BaseModel):
    """Базовая схема слова."""
    word: str = Field(..., min_length=1, max_length=100, description="Слово")
    translation: Optional[str] = Field(None, max_length=500, description="Перевод")
    status: VocabularyStatus = VocabularyStatus.LEARNING


class VocabularyCreate(VocabularyBase):
    """Данные для добавления слова."""
    pass

    class Config:
        json_schema_extra = {
            "example": {
                "word": "学习",
                "translation": "учить, изучать",
                "status": "learning",
            }
        }


class VocabularyUpdate(BaseModel):
    """Данные для обновления слова."""
    word: Optional[str] = Field(None, min_length=1, max_length=100)
    translation: Optional[str] = Field(None, max_length=500)
    status: Optional[VocabularyStatus] = None


class VocabularyResponse(VocabularyBase):
    """Информация о слове в словаре."""
    id: int
    user_id: int
    last_seen: Optional[datetime] = None
    seen_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class VocabularyList(BaseModel):
    """Список слов с пагинацией."""
    items: List[VocabularyResponse]
    total: int
    page: int
    size: int
