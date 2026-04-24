"""
Сервис анализа текста.
Интеграция с Go микросервисом и обработка результатов.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models.models import TextModel, Token, UserVocabulary, VocabularyStatus
from services.go_client import go_analyzer


def analyze_text_in_go(
    text: str,
    language: str = "zh",
    user_level: int = 1,
) -> Optional[Dict[str, Any]]:
    """
    Отправить текст на анализ в Go микросервис.

    Args:
        text: Текст для анализа
        language: Код языка
        user_level: Уровень пользователя (HSK)

    Returns:
        Результаты анализа или None при ошибке
    """
    return go_analyzer.analyze_text(
        text=text,
        language=language,
        user_level=user_level,
    )


def save_tokens_to_db(
    db: Session,
    text_id: int,
    tokens_data: List[Dict[str, Any]],
) -> int:
    """
    Сохранить токены в базу данных.

    Args:
        db: Сессия БД
        text_id: ID текста
        tokens_data: Список токенов с метаданными

    Returns:
        Количество сохранённых токенов
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Удалить старые токены
    db.query(Token).filter(Token.text_id == text_id).delete()

    # Сохранить новые токены
    saved_count = 0
    for token_data in tokens_data:
        # Берём первую позицию из массива positions
        positions = token_data.get("positions", [])
        logger.info(f"Token {token_data.get('value')}: positions={positions}, type={type(positions)}")
        position = positions[0] if positions and len(positions) > 0 else None
        
        token = Token(
            text_id=text_id,
            value=token_data.get("value", ""),
            lemma=token_data.get("lemma", ""),
            position=position,
            frequency=token_data.get("frequency", 1),
        )
        db.add(token)
        saved_count += 1

    db.commit()
    logger.info(f"Saved {saved_count} tokens")
    return saved_count


def get_known_words(db: Session, user_id: int) -> set:
    """
    Получить множество известных слов пользователя.

    Args:
        db: Сессия БД
        user_id: ID пользователя

    Returns:
        Множество известных слов
    """
    vocab = db.query(UserVocabulary).filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.status == VocabularyStatus.KNOW,
    ).all()
    return {v.word for v in vocab}


def analyze_text(
    db: Session,
    text_id: int,
    user_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Полный анализ текста с интеграцией Go сервиса и БД.

    Args:
        db: Сессия БД
        text_id: ID текста
        user_id: ID пользователя

    Returns:
        Результаты анализа с метками известных слов
    """
    # Найти текст
    text = db.query(TextModel).filter(TextModel.id == text_id).first()
    if not text:
        return None

    # Получить известные слова пользователя
    known_words = get_known_words(db, user_id)

    # Получить токены из БД (если уже сохранены)
    tokens = db.query(Token).filter(Token.text_id == text_id).all()

    result_tokens = []
    for token in tokens:
        result_tokens.append({
            "value": token.value,
            "lemma": token.lemma,
            "frequency": token.frequency,
            "position": token.position,
            "is_known": token.value in known_words,
        })

    return {
        "text_id": text.id,
        "content": text.content,
        "language": text.language,
        "tokens": result_tokens,
        "tokens_count": len(tokens),
    }


def tokenize_text(text: str, lang: str = "zh") -> List[str]:
    """
    Локальная токенизация (fallback если Go сервис недоступен).

    Args:
        text: Текст для токенизации
        lang: Код языка

    Returns:
        Список токенов
    """
    import jieba

    if lang.startswith("zh"):
        tokens = list(jieba.cut(text, cut_all=False))
        return [t for t in tokens if t.strip()]
    else:
        return text.split()
