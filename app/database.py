"""
Конфигурация базы данных.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Поддержка SQLite для разработки и PostgreSQL для продакшена
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./user.db"
)

# Для PostgreSQL раскомментировать:
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://user:password@localhost:5432/langdb"
# )

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency для получения сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация таблиц БД."""
    # Импортируем модели для регистрации
    from models import models  # noqa: F401

    Base.metadata.create_all(engine)
