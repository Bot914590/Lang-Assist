"""
Модели базы данных.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Text as SAText, ForeignKey,
    Float, func, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.database import Base
from passlib.context import CryptContext

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    lang_level = Column(String(20), nullable=True)  # Уровень языка (HSK 1-6, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    vocab = relationship("UserVocabulary", back_populates="user", cascade="all, delete-orphan")
    texts = relationship("TextModel", back_populates="user", cascade="all, delete-orphan")

    # Методы работы с паролем
    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)


class TextModel(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(SAText, nullable=False)
    language = Column(String(8), nullable=False, default="zh")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Account", back_populates="texts")
    tokens = relationship("Token", back_populates="text", cascade="all, delete-orphan")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    text_id = Column(Integer, ForeignKey("texts.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(String(200), nullable=False, index=True)
    lemma = Column(String(200), nullable=True)
    position = Column(Integer, nullable=True)
    frequency = Column(Integer, default=1, nullable=False)

    text = relationship("TextModel", back_populates="tokens")


class VocabularyStatus(PyEnum):
    """Статус слова в словаре."""
    KNOW = "known"
    LEARNING = "learning"
    IGNORED = "ignored"


class UserVocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    word = Column(String(200), nullable=False, index=True)
    translation = Column(String(500), nullable=True)
    status = Column(SQLEnum(VocabularyStatus), default=VocabularyStatus.LEARNING, nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    seen_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Account", back_populates="vocab")

    __table_args__ = (
        UniqueConstraint("user_id", "word", name="uix_user_word"),
    )


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    word = Column(String(200), nullable=False, index=True)
    context = Column(SAText, nullable=True)
    translation = Column(String(1000), nullable=True)
    easiness_factor = Column(Float, default=2.5, nullable=False)
    interval = Column(Integer, default=0, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)
    next_review = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Account", back_populates="flashcards")
    reviews = relationship("Review", back_populates="flashcard", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, index=True)
    quality = Column(Integer, nullable=False)  # 0-5
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    flashcard = relationship("Flashcard", back_populates="reviews")
