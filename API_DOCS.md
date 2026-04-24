# API Документация Language Assist

## Interactive Documentation

После запуска сервера доступна интерактивная документация:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## FastAPI Endpoints

### Health Check

**GET** `/health`

Проверка доступности API.

**Ответ:**
```json
{"status": "ok"}
```

---

### Тексты

#### Создать текст
**POST** `/api/v1/texts`

**Request:**
```json
{
  "content": "我喜欢学习中文。今天天气很好。",
  "language": "zh"
}
```

**Валидация:**
- `content`: 1-10000 символов
- `language`: код языка (zh, en, etc.)

**Response:** `UserTextOutput`

---

#### Анализ текста (с fallback)
**POST** `/api/v1/texts/{text_id}/analyze`

Анализирует текст через Go сервис. Если Go сервис недоступен, используется fallback на jieba.

**Response:**
```json
{
  "status": "ok",
  "text_id": 1,
  "tokens_count": 22,
  "tokens_created": 18
}
```

**Статусы:**
- `ok` - анализ через Go сервис
- `ok (fallback)` - анализ через jieba (Go сервис недоступен)

---

#### Упрощение текста
**POST** `/api/v1/texts/{text_id}/simplify`

Упрощает текст до целевого уровня HSK, заменяя сложные слова на простые аналоги.

**Request:**
```json
{
  "target_level": 2
}
```

**Response:**
```json
{
  "status": "ok",
  "original_text": "她很美丽",
  "simplified_text": "她很漂亮",
  "replacements": [
    {
      "original": "美丽",
      "replacement": "漂亮",
      "reason": "HSK level too high",
      "hsk_level": 4,
      "similarity": 0.70
    }
  ],
  "target_level": 2,
  "total_tokens": 3,
  "replaced_count": 1
}
```

---

### Пользователи

#### Регистрация
**POST** `/api/v1/users/register`

**Request:**
```json
{
  "email": "user@example.com",
  "username": "user123",
  "password": "password123",
  "lang_level": "HSK 2"
}
```

---

#### Вход
**POST** `/api/v1/users/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

---

### Словарь

#### Добавить слово
**POST** `/api/v1/vocabulary`

**Request:**
```json
{
  "word": "学习",
  "translation": "учить, изучать",
  "status": "learning"
}
```

---

#### Получить словарь
**GET** `/api/v1/vocabulary?page=1&size=20&status=learning`

**Параметры:**
- `page`: номер страницы (default: 1)
- `size`: размер страницы (1-100, default: 20)
- `status`: фильтр по статусу (known, learning, ignored)

**Response:**
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "size": 20
}
```

---

### Карточки

#### Генерация из текста
**POST** `/api/v1/flashcards/generate`

Автоматически создаёт карточки для незнакомых слов из текста.

**Request:**
```json
{"text_id": 1}
```

**Response:**
```json
{
  "status": "ok",
  "text_id": 1,
  "cards_created": 5,
  "cards_skipped": 10,
  "flashcards": [...]
}
```

---

#### Повторение карточки
**POST** `/api/v1/flashcards/{card_id}/review`

Оценка знания карточки по системе SM-2.

**Request:**
```json
{"quality": 4}
```

**Шкала оценок:**
- 0 - Полный провал, не помню ничего
- 1 - Почти не помню
- 2 - Трудно вспомнить
- 3 - Нормально вспомнил
- 4 - Хорошо помню
- 5 - Отлично, уверенно

**Алгоритм SM-2:**
- При оценке < 3: интервал сбрасывается на 1 день
- При оценке >= 3: интервал увеличивается по формуле
- EF (Easiness Factor) корректируется на основе качества

---

## Go Analyzer API

### Анализ текста
**POST** `/analyze`

**Request:**
```json
{
  "text": "我喜欢学习中文",
  "lang": "zh",
  "user_level": 2
}
```

**Response:**
```json
{
  "status": "ok",
  "tokens_count": 7,
  "tokens": [
    {
      "value": "我",
      "lemma": "我",
      "frequency": 1,
      "positions": [0],
      "hsk": 1,
      "is_known": true
    }
  ]
}
```

---

### Упрощение текста
**POST** `/simplify`

**Request:**
```json
{
  "text": "这个经济问题很复杂",
  "target_level": 2
}
```

**Response:**
```json
{
  "status": "ok",
  "original_text": "这个经济问题很复杂",
  "simplified_text": "这个经济问题很 [COMPLEX:4]",
  "replacements": [
    {
      "original": "经济",
      "replacement": "[COMPLEX:4]",
      "reason": "HSK level too high, no similar word found",
      "hsk_level": 4,
      "similarity": 0
    }
  ],
  "target_level": 2,
  "total_tokens": 6,
  "replaced_count": 2
}
```

---

### Информация о слове
**GET** `/word/info?word={word}`

**Параметры:**
- `word`: китайское слово

**Response:**
```json
{
  "word": "学习",
  "hsk_level": 3,
  "pinyin": "xué xí",
  "strokes": "",
  "translations": {
    "eng": ["to learn", "to study"],
    "rus": ["учить", "изучать"]
  },
  "has_embedding": true
}
```

---

### Похожие слова
**GET** `/word/similar?word={word}&max_level={level}&top_k={k}`

**Параметры:**
- `word`: исходное слово
- `max_level`: максимальный уровень HSK (default: 4)
- `top_k`: количество результатов (default: 10)

**Response:**
```json
{
  "word": "美丽",
  "max_level": 2,
  "similar": [
    {
      "word": "漂亮",
      "similarity": 0.70,
      "hsk_level": 1
    },
    {
      "word": "好",
      "similarity": 0.55,
      "hsk_level": 1
    }
  ]
}
```

---

### Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "ok",
  "hsk_loaded": true,
  "embeddings": true,
  "vector_size": 200,
  "max_hsk_level": 4
}
```

---

## Переменные окружения

| Переменная | Описание | Default |
|------------|----------|---------|
| `DATABASE_URL` | URL базы данных | `sqlite:///./user.db` |
| `DB_ECHO` | Логирование SQL | `false` |
| `GO_ANALYZER_URL` | URL Go сервиса | `http://localhost:8080` |
| `GO_ANALYZER_TIMEOUT` | Таймаут (сек) | `30.0` |
| `GO_ANALYZER_MAX_RETRIES` | Попыток retry | `3` |
| `GO_ANALYZER_RETRY_DELAY` | Задержка retry (сек) | `1.0` |
| `CORS_ORIGINS` | CORS origins | `*` |

---

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успех |
| 201 | Создано |
| 204 | Удалено |
| 400 | Некорректный запрос |
| 404 | Не найдено |
| 409 | Конфликт (дубликат) |
| 503 | Сервис недоступен |

---

## Примеры использования

### Полный цикл работы

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'

# 2. Создание текста
curl -X POST http://localhost:8000/api/v1/texts \
  -H "Content-Type: application/json" \
  -d '{"content":"我喜欢学习中文","language":"zh"}'

# 3. Анализ текста
curl -X POST http://localhost:8000/api/v1/texts/1/analyze

# 4. Генерация карточек
curl -X POST http://localhost:8000/api/v1/flashcards/generate \
  -H "Content-Type: application/json" \
  -d '{"text_id":1}'

# 5. Повторение карточки
curl -X POST http://localhost:8000/api/v1/flashcards/1/review \
  -H "Content-Type: application/json" \
  -d '{"quality":4}'

# 6. Упрощение текста
curl -X POST http://localhost:8000/api/v1/texts/1/simplify \
  -H "Content-Type: application/json" \
  -d '{"target_level":2}'
```
