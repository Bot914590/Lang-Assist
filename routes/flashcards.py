"""
Маршруты для работы с карточками (Flashcards) и системой повторения SM-2.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from models.models import Flashcard, Review, TextModel, Token, UserVocabulary, VocabularyStatus
from schemas.flashcards import (
    FlashcardCreate,
    FlashcardResponse,
    FlashcardList,
    ReviewCreate,
    ReviewResponse,
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
)
from services.sm2 import calculate_next_review

router = APIRouter()


@router.post("/flashcards/generate", response_model=GenerateFlashcardsResponse)
def generate_flashcards_from_text(
    request: GenerateFlashcardsRequest,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Сгенерировать карточки из текста на основе неизвестных слов.
    """
    # Найти текст
    text = db.query(TextModel).filter(TextModel.id == request.text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")

    # Получить токены текста
    tokens = db.query(Token).filter(Token.text_id == text.id).all()

    # Получить известные слова пользователя
    known_words = db.query(UserVocabulary.word).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.status == VocabularyStatus.KNOW,
    ).all()
    known_words_set = {w[0] for w in known_words}

    # Получить слова из словаря с переводом
    vocab_dict = {
        v.word: v
        for v in db.query(UserVocabulary).filter(
            UserVocabulary.user_id == user_id,
            UserVocabulary.status == VocabularyStatus.LEARNING,
        ).all()
    }

    created_cards = []
    skipped_count = 0

    for token in tokens:
        word = token.value

        # Пропустить если слово уже известно или это пунктуация
        if word in known_words_set or len(word) < 2:
            skipped_count += 1
            continue

        # Проверить, нет ли уже карточки с этим словом
        existing_card = db.query(Flashcard).filter(
            Flashcard.user_id == user_id,
            Flashcard.word == word,
        ).first()

        if existing_card:
            skipped_count += 1
            continue

        # Получить перевод из словаря или оставить пустым
        translation = vocab_dict.get(word, None)
        translation_text = translation.translation if translation else None

        # Создать карточку
        flashcard = Flashcard(
            user_id=user_id,
            word=word,
            context=text.content[:200] if len(text.content) > 200 else text.content,
            translation=translation_text,
            easiness_factor=2.5,
            interval=0,
            repetitions=0,
            next_review=datetime.now(),  # Сразу доступно для повторения
        )

        db.add(flashcard)
        created_cards.append(flashcard)

        # Добавить слово в словарь если ещё нет
        if word not in vocab_dict:
            new_vocab = UserVocabulary(
                user_id=user_id,
                word=word,
                status=VocabularyStatus.LEARNING,
                last_seen=datetime.now(),
                seen_count=0,
            )
            db.add(new_vocab)

    db.commit()

    # Обновить данные карточек после commit
    for card in created_cards:
        db.refresh(card)

    return GenerateFlashcardsResponse(
        status="ok",
        text_id=request.text_id,
        cards_created=len(created_cards),
        cards_skipped=skipped_count,
        flashcards=created_cards,
    )


@router.post("/flashcards", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
def create_flashcard(
    card_in: FlashcardCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Создать карточку вручную.
    """
    flashcard = Flashcard(
        user_id=user_id,
        word=card_in.word,
        context=card_in.context,
        translation=card_in.translation,
        easiness_factor=2.5,
        interval=0,
        repetitions=0,
        next_review=datetime.now(),
    )

    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)

    return flashcard


@router.get("/flashcards", response_model=FlashcardList)
def get_flashcards(
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
    due_only: bool = Query(False, description="Только карточки для повторения"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """
    Получить карточки пользователя.
    """
    query = db.query(Flashcard).filter(Flashcard.user_id == user_id)

    if due_only:
        now = datetime.now()
        query = query.filter(
            Flashcard.next_review <= now,
        )

    total = query.count()
    items = query.order_by(Flashcard.next_review).offset((page - 1) * size).limit(size).all()

    return FlashcardList(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/flashcards/{card_id}", response_model=FlashcardResponse)
def get_flashcard(
    card_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Получить конкретную карточку.
    """
    card = db.query(Flashcard).filter(
        Flashcard.id == card_id,
        Flashcard.user_id == user_id,
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    return card


@router.post("/flashcards/{card_id}/review", response_model=ReviewResponse)
def review_flashcard(
    card_id: int,
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Пройти повторение карточки (оценка 0-5 по системе SM-2).
    """
    card = db.query(Flashcard).filter(
        Flashcard.id == card_id,
        Flashcard.user_id == user_id,
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Рассчитать новые параметры по SM-2
    result = calculate_next_review(
        quality=review_in.quality,
        easiness_factor=card.easiness_factor,
        interval=card.interval,
        repetitions=card.repetitions,
    )

    # Обновить карточку
    card.easiness_factor = result["easiness_factor"]
    card.interval = result["interval"]
    card.repetitions = result["repetitions"]
    card.next_review = result["next_review"]

    # Создать запись о повторении
    review = Review(
        flashcard_id=card.id,
        quality=review_in.quality,
    )
    db.add(review)

    # Обновить счётчик в словаре
    vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.word == card.word,
    ).first()

    if vocab:
        vocab.seen_count += 1
        vocab.last_seen = datetime.now()
        if review_in.quality >= 3:
            vocab.status = VocabularyStatus.KNOW

    db.commit()
    db.refresh(card)
    db.refresh(review)

    return review


@router.get("/flashcards/{card_id}/reviews", response_model=List[ReviewResponse])
def get_flashcard_reviews(
    card_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Получить историю повторений карточки.
    """
    card = db.query(Flashcard).filter(
        Flashcard.id == card_id,
        Flashcard.user_id == user_id,
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    reviews = db.query(Review).filter(Review.flashcard_id == card_id).all()
    return reviews


@router.delete("/flashcards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(
    card_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Удалить карточку.
    """
    card = db.query(Flashcard).filter(
        Flashcard.id == card_id,
        Flashcard.user_id == user_id,
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    db.delete(card)
    db.commit()
