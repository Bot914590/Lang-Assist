"""
Маршруты для работы с текстами.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from models.models import TextModel, Token, Account
from schemas.text import (
    UserTextInput,
    UserTextOutput,
    TextAnalyzeResponse,
    TokenData,
    SimplifyRequest,
    SimplifyResponse,
)
from services.analyze import analyze_text_in_go, save_tokens_to_db, analyze_text
from services.go_client import go_analyzer, go_simplifier

router = APIRouter()


@router.post("/texts", response_model=UserTextOutput, status_code=status.HTTP_201_CREATED)
def create_text(
    text_in: UserTextInput,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,  # Для MVP, потом из токена
):
    """
    Загрузить/вставить новый текст.
    """
    # Валидация контента
    if not text_in.content or len(text_in.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text content cannot be empty")
    
    if len(text_in.content) > 10000:
        raise HTTPException(status_code=400, detail="Text content too long (max 10000 characters)")
    
    # Определение языка (простая эвристика)
    language = text_in.language or "zh"

    new_text = TextModel(
        content=text_in.content,
        created_at=datetime.now(),
        user_id=user_id,
        language=language,
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    return new_text


@router.get("/texts", response_model=List[UserTextOutput])
def get_texts(
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,  # Для MVP
):
    """
    Получить все тексты пользователя.
    """
    texts = db.query(TextModel).filter(TextModel.user_id == user_id).all()
    return texts


@router.get("/texts/{text_id}", response_model=UserTextOutput)
def get_text(
    text_id: int,
    db: Session = Depends(get_db),
):
    """
    Получить текст по ID.
    """
    text = db.query(TextModel).filter(TextModel.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")
    return text


@router.post("/texts/{text_id}/analyze", response_model=TextAnalyzeResponse)
def analyze_text_endpoint(
    text_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
    user_level: Optional[int] = 1,
):
    """
    Анализ текста: токенизация через Go микросервис (с fallback на jieba).
    """
    # Найти текст
    text = db.query(TextModel).filter(TextModel.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")

    # Отправить на анализ в Go сервис (с fallback)
    go_result = go_analyzer.analyze_text_with_fallback(
        text=text.content,
        language=text.language,
        user_level=user_level,
    )

    if not go_result or go_result.get("status") is None:
        raise HTTPException(
            status_code=503,
            detail="Text analysis failed: both Go service and fallback unavailable",
        )

    # Сохранить токены в БД
    tokens_data = go_result.get("tokens", [])
    tokens_created = save_tokens_to_db(db, text_id, tokens_data)

    is_fallback = go_result.get("fallback", False)

    # Преобразовать токены в формат схемы - берём напрямую из Go ответа
    from schemas.text import TokenData
    token_models = []
    for t in tokens_data:
        positions = t.get("positions", [])
        token_models.append(TokenData(
            value=t.get("value"),
            lemma=t.get("lemma"),
            frequency=t.get("frequency", 1),
            position=positions[0] if positions else None,
            is_known=t.get("is_known", False),
            hsk=t.get("hsk"),
        ))

    return TextAnalyzeResponse(
        status="ok" if not is_fallback else "ok (fallback)",
        text_id=text_id,
        tokens_count=go_result.get("tokens_count", 0),
        tokens_created=tokens_created,
        tokens=token_models,
    )


@router.get("/texts/{text_id}/analyze", response_model=TextAnalyzeResponse)
def get_text_analysis(
    text_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = 1,
):
    """
    Получить результаты анализа текста.
    """
    result = analyze_text(db=db, text_id=text_id, user_id=user_id)

    if not result:
        raise HTTPException(status_code=404, detail="Text or analysis not found")

    # Преобразовать токены в формат схемы
    tokens = result.get("tokens", [])
    token_models = [TokenData(**t) for t in tokens]

    return TextAnalyzeResponse(
        status="ok",
        text_id=text_id,
        content=result.get("content"),
        tokens_count=result.get("tokens_count", 0),
        tokens=token_models,
    )


@router.post("/texts/{text_id}/simplify", response_model=SimplifyResponse)
def simplify_text_endpoint(
    text_id: int,
    request: SimplifyRequest,  # Теперь только target_level
    db: Session = Depends(get_db),
):
    """
    Упростить текст до целевого уровня HSK.
    """
    # Найти текст
    text = db.query(TextModel).filter(TextModel.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")

    # Отправить на упрощение в Go сервис (simplifier)
    go_result = go_simplifier.simplify_text(
        text=text.content,
        target_level=request.target_level,
        language=text.language,
    )

    if not go_result or go_result.get("status") != "ok":
        error_detail = "Go simplifier service unavailable"
        if go_result and "error" in go_result:
            error_detail = go_result["error"]
        raise HTTPException(
            status_code=503,
            detail=error_detail,
        )

    return SimplifyResponse(
        status=go_result.get("status"),
        original_text=go_result.get("original_text"),
        simplified_text=go_result.get("simplified_text"),
        replacements=go_result.get("replacements", []),
        target_level=go_result.get("target_level"),
        total_tokens=go_result.get("total_tokens"),
        replaced_count=go_result.get("replaced_count"),
    )


@router.post("/texts/simplify", response_model=SimplifyResponse)
def simplify_text_direct(
    request: SimplifyRequestDirect,
):
    """
    Упростить текст напрямую через Go сервис (без сохранения в БД).
    """
    go_result = go_simplifier.simplify_text(
        text=request.text,
        target_level=request.target_level,
        language=request.language,
    )

    if not go_result or go_result.get("status") != "ok":
        raise HTTPException(
            status_code=503,
            detail="Go simplifier service unavailable",
        )

    return SimplifyResponse(
        status=go_result.get("status"),
        original_text=go_result.get("original_text"),
        simplified_text=go_result.get("simplified_text"),
        replacements=go_result.get("replacements", []),
        target_level=go_result.get("target_level"),
        total_tokens=go_result.get("total_tokens"),
        replaced_count=go_result.get("replaced_count"),
    )


@router.delete("/texts/{text_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_text(
    text_id: int,
    db: Session = Depends(get_db),
):
    """
    Удалить текст и все связанные токены.
    """
    text = db.query(TextModel).filter(TextModel.id == text_id).first()
    if not text:
        raise HTTPException(status_code=404, detail="Text not found")

    db.delete(text)
    db.commit()
