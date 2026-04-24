from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database import init_db

from routes import texts, users, vocabulary, flashcards

app = FastAPI(title="Language Assist API", version="1.0.0")

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Для продакшена указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# Подключение роутов
app.include_router(texts.router, prefix="/api/v1", tags=["texts"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(vocabulary.router, prefix="/api/v1", tags=["vocabulary"])
app.include_router(flashcards.router, prefix="/api/v1", tags=["flashcards"])
