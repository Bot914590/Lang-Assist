# Language Assist

MVP приложения для изучения языков с анализом текстов, токенизацией, и системой повторения карточек (SM-2).

## старт с Docker

```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Или вручную
docker-compose up -d --build
```

Сервисы будут доступны по адресам:
- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **Go Analyzer**: http://localhost:8080
- **Go Simplifier**: http://localhost:8081

 Полная инструкция: [DOCKER_INSTRUCTION.md](DOCKER_INSTRUCTION.md)

## Архитектура

```
┌──────────────────────────────────────────┐
│          docker-compose.yml              │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  API (FastAPI Python) :8000     │    │
│  └─────────┬───────────────────────┘    │
│            │                            │
│     ┌──────┴──────┐                     │
│     │             │                     │
│  ┌──▼──┐     ┌───▼────────┐            │
│  │Ana- │     │Simplifier  │            │
│  │lyzer│     │   (Go)     │            │
│  │(Go) │     │  :8081     │            │
│  │:8080│     │            │            │
│  └─────┘     └────────────┘            │
└──────────────────────────────────────────┘
```

## Компоненты

### 1. FastAPI Бэкенд (порт 8000)
- REST API для управления текстами, словарём, карточками
- Интеграция с Go микросервисами для анализа и упрощения текста
- Алгоритм SM-2 для расчёта интервалов повторения
- JWT аутентификация

### 2. Go Analyzer (порт 8080)
- Токенизация текстов (китайский, европейские языки)
- Лемматизация
- Определение уровня HSK
- Выделение известных/незнакомых слов
- Расчёт частотности токенов

### 3. Go Simplifier (порт 8081)
- Упрощение текстов до целевого уровня HSK
- Замена сложных слов на более простые
- Сохранение контекста

### 4. База данных
- SQLite (для разработки)
- PostgreSQL (для продакшена)

## Запуск

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Автоматически
./start.sh        # Linux/Mac
start.bat         # Windows

# Или вручную
docker-compose up -d --build
```

Проверка статуса:
```bash
docker-compose ps
docker-compose logs -f
```

Остановка:
```bash
docker-compose down
```

 Полная документация: [DOCKER_INSTRUCTION.md](DOCKER_INSTRUCTION.md), [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

### Вариант 2: Локальный запуск

#### FastAPI
```bash
cd C:\vscode\Language_assist
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Go микросервис
```bash
cd analyzer-go
go run main.go
```

## API Endpoints

### Health Check
```
GET /health
```

### Тексты
```
POST   /api/v1/texts              # Загрузить текст
GET    /api/v1/texts              # Список текстов
GET    /api/v1/texts/{id}         # Текст по ID
POST   /api/v1/texts/{id}/analyze # Анализировать текст
GET    /api/v1/texts/{id}/analyze # Результаты анализа
DELETE /api/v1/texts/{id}         # Удалить текст
```

### Пользователи
```
POST /api/v1/users/register       # Регистрация
POST /api/v1/users/login          # Вход
GET  /api/v1/users/me             # Профиль
PUT  /api/v1/users/me             # Обновить профиль
```

### Словарь
```
GET    /api/v1/vocabulary         # Список слов
POST   /api/v1/vocabulary         # Добавить слово
GET    /api/v1/vocabulary/{word}  # Слово из словаря
PUT    /api/v1/vocabulary/{word}  # Обновить слово
DELETE /api/v1/vocabulary/{word}  # Удалить слово
```

### Карточки
```
POST /api/v1/flashcards/generate          # Генерация из текста
POST /api/v1/flashcards                   # Создать карточку
GET  /api/v1/flashcards                   # Список карточек
GET  /api/v1/flashcards/{id}              # Карточка по ID
POST /api/v1/flashcards/{id}/review       # Повторение (0-5)
GET  /api/v1/flashcards/{id}/reviews      # История повторений
DELETE /api/v1/flashcards/{id}            # Удалить карточку
```

## Примеры запросов

### 1. Загрузка текста
```bash
curl -X POST http://localhost:8000/api/v1/texts \
  -H "Content-Type: application/json" \
  -d '{"content": "我喜欢学习中文。今天天气很好。", "language": "zh"}'
```

### 2. Анализ текста
```bash
curl -X POST http://localhost:8000/api/v1/texts/1/analyze
```

### 3. Генерация карточек
```bash
curl -X POST http://localhost:8000/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{"text_id": 1}'
```

### 4. Повторение карточки
```bash
curl -X POST http://localhost:8000/api/v1/flashcards/1/review \
  -H "Content-Type: application/json" \
  -d '{"quality": 4}'
```

### 5. Получение карточек для повторения
```bash
curl http://localhost:8000/api/v1/flashcards?due_only=true
```

## Go Analyzer API

### Анализ текста
```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "我喜欢学习中文", "lang": "zh", "user_level": 2}'
```

### Health check
```bash
curl http://localhost:8080/health
```
