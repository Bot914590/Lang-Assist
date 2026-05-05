# Деплой на Railway

## Предварительные требования
1. Аккаунт на [Railway.app](https://railway.app)
2. Проект загружен в GitHub репозиторий

## Шаги

### 1. Создание проекта на Railway
```bash
# Через CLI
railway login
railway init
```

Или через веб-интерфейс: New Project → Connect GitHub repo

### 2. Настройка переменных окружения

В Railway Dashboard перейди в Variables и добавь:

```
DATABASE_URL=sqlite:///./user.db
API_KEYS=твой-секретный-ключ
JWT_SECRET_KEY=сгенерируй-новый-секретный-ключ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GO_ANALYZER_URL=http://analyzer:8080
GO_SIMPLIFIER_URL=http://simplifier:8081
PORT=8000
```

### 3. Деплой

Railway автоматически определит `docker-compose.yml` и запустит все 3 сервиса:
- `api` (Python FastAPI)
- `analyzer` (Go)
- `simplifier` (Go)

### 4. Проверка

После деплоя открой URL:
- `https://твой-проект.up.railway.app/health`
- `https://твой-проект.up.railway.app/api/v1/simplify`

## Устранение проблем

### Не собирается Go
Проверь что в `analyzer-go/` и `golern-go/` есть `go.mod` и `go.sum`

### База данных
Railway предоставляет PostgreSQL. Для использования:
1. Создай Railway MySQL/PostgreSQL plugin
2. Скопируй DATABASE_URL в переменные

### Лимиты
- Бесплатный план: $5/месяц кредитов
- Сервисы не "усыпают" (в отличие от Render)

## Команды Railway CLI
```bash
railway login
railway init
railway up
railway logs
railway status
```