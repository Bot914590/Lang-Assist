"""
Маршруты для работы со словарём пользователя.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from models.models import UserVocabulary, VocabularyStatus, Account
from schemas.vocabulary import (
    VocabularyCreate,
    VocabularyUpdate,
    VocabularyResponse,
    VocabularyList,
)

router = APIRouter()


@router.post("/vocabulary", response_model=VocabularyResponse, status_code=status.HTTP_201_CREATED)
def add_word_to_vocabulary(
    vocab_in: VocabularyCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,  # Для MVP
):
    """
    Добавить слово в словарь пользователя.
    """
    # Проверка на дубликат
    existing = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.word == vocab_in.word,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Word already in vocabulary")

    new_word = UserVocabulary(
        user_id=user_id,
        word=vocab_in.word,
        status=VocabularyStatus(vocab_in.status) if vocab_in.status else VocabularyStatus.LEARNING,
        last_seen=datetime.now(),
        seen_count=0,
    )

    db.add(new_word)
    db.commit()
    db.refresh(new_word)

    return new_word


@router.get("/vocabulary", response_model=VocabularyList)
def get_vocabulary(
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
    status_filter: Optional[VocabularyStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """
    Получить словарь пользователя с фильтрацией и пагинацией.
    """
    query = db.query(UserVocabulary).filter(UserVocabulary.user_id == user_id)

    if status_filter:
        query = query.filter(UserVocabulary.status == status_filter)

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return VocabularyList(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/vocabulary/{word}", response_model=VocabularyResponse)
def get_word_from_vocabulary(
    word: str,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Получить конкретное слово из словаря.
    """
    vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.word == word,
    ).first()

    if not vocab:
        raise HTTPException(status_code=404, detail="Word not found in vocabulary")

    return vocab


@router.put("/vocabulary/{word}", response_model=VocabularyResponse)
def update_word_in_vocabulary(
    word: str,
    vocab_update: VocabularyUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Обновить слово в словаре (статус, перевод).
    """
    vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.word == word,
    ).first()

    if not vocab:
        raise HTTPException(status_code=404, detail="Word not found in vocabulary")

    update_data = vocab_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "status" and value:
            vocab.status = VocabularyStatus(value)
        elif hasattr(vocab, field):
            setattr(vocab, field, value)

    db.commit()
    db.refresh(vocab)

    return vocab


@router.delete("/vocabulary/{word}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word_from_vocabulary(
    word: str,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Удалить слово из словаря.
    """
    vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.word == word,
    ).first()

    if not vocab:
        raise HTTPException(status_code=404, detail="Word not found in vocabulary")

    db.delete(vocab)
    db.commit()


@router.post("/vocabulary/{word}/set-status")
def set_word_status(
    word: str,
    status_new: VocabularyStatus,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Установить статус слова (known, learning, ignored).
    """
    vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.word == word,
    ).first()

    if not vocab:
        raise HTTPException(status_code=404, detail="Word not found in vocabulary")

    vocab.status = status_new
    db.commit()
    db.refresh(vocab)

    return vocab
