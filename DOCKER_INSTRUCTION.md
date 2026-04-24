# Language Assist - Docker Инструкция

## ✅ Что было сделано

1. **Возвращён Go Simplifier** в код бэкенда
2. **Созданы Dockerfile** для всех 3 сервисов:
   - `Dockerfile.api` - Python FastAPI (порт 8000)
   - `Dockerfile.analyzer` - Go Analyzer (порт 8080)
   - `Dockerfile.simplifier` - Go Simplifier (порт 8081)
3. **Создан docker-compose.yml** для оркестрации
4. **Обновлено расширение** - вызывает упрощение текста
5. **Создана документация** - DOCKER_DEPLOYMENT.md

## 🚀 Как запускать

### Вариант 1: Автоматически (Windows)

```cmd
cd C:\vscode\Language_assist
start.bat
```

### Вариант 2: Автоматически (Linux/Mac)

```bash
cd /path/to/Language_assist
chmod +x start.sh
./start.sh
```

### Вариант 3: Вручную

```bash
# 1. Перейдите в директорию проекта
cd C:\vscode\Language_assist

# 2. Создайте .env файл
cp .env.example .env

# 3. Отредактируйте .env (измените JWT_SECRET_KEY)
notepad .env

# 4. Запустите все сервисы
docker-compose up -d --build

# 5. Проверьте статус
docker-compose ps

# 6. Посмотрите логи
docker-compose logs -f
```

## 📍 Сервисы доступны по адресам

| Сервис | URL | Описание |
|--------|-----|----------|
| **API** | http://localhost:8000 | FastAPI бэкенд |
| **Docs** | http://localhost:8000/docs | Swagger документация |
| **Analyzer** | http://localhost:8080 | Go токенизация |
| **Simplifier** | http://localhost:8081 | Go упрощение текста |

## 🧪 Тестирование

### 1. Проверка API

```bash
curl http://localhost:8000/health
```

### 2. Проверка Analyzer

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"你好世界","lang":"zh","user_level":1}'
```

### 3. Проверка Simplifier

```bash
curl -X POST http://localhost:8081/simplify \
  -H "Content-Type: application/json" \
  -d '{"text":"她很美丽","lang":"zh","target_level":2}'
```

### 4. Полный тест через API

```bash
# Создание текста
curl -X POST http://localhost:8000/api/v1/texts \
  -H "Content-Type: application/json" \
  -d '{"content":"你好世界","language":"zh"}'

# Анализ (должно вернуть токены)
curl -X POST http://localhost:8000/api/v1/texts/1/analyze \
  -H "Content-Type: application/json"

# Упрощение (должно вернуть упрощённый текст)
curl -X POST http://localhost:8000/api/v1/texts/1/simplify \
  -H "Content-Type: application/json" \
  -d '{"target_level": 2}'
```

## 🛑 Остановка

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить данные (база данных будет удалена!)
docker-compose down -v
```

## 📊 Архитектура

```
┌──────────────────────────────────────────┐
│          docker-compose.yml              │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  API (FastAPI Python) :8000     │    │
│  │  - routes/users.py              │    │
│  │  - routes/texts.py              │    │
│  │  - services/go_client.py        │    │
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

## 🔧 Управление

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f api
docker-compose logs -f analyzer
docker-compose logs -f simplifier
```

### Перезапуск

```bash
# Все сервисы
docker-compose restart

# Конкретный сервис
docker-compose restart api
```

### Вход в контейнер

```bash
# API
docker-compose exec api bash

# Analyzer
docker-compose exec analyzer sh

# Simplifier
docker-compose exec simplifier sh
```

### Мониторинг

```bash
# Статус
docker-compose ps

# Использование ресурсов
docker stats
```

## 📝 Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL базы данных | `sqlite:///./user.db` |
| `GO_ANALYZER_URL` | URL Go Analyzer | `http://analyzer:8080` |
| `GO_SIMPLIFIER_URL` | URL Go Simplifier | `http://simplifier:8081` |
| `JWT_SECRET_KEY` | Секретный ключ JWT | `your-secret-key...` |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `1440` |

## 🐛 Отладка

### Сервис не запускается

```bash
# Проверка логов
docker-compose logs api

# Проверка места на диске
df -h

# Очистка Docker
docker system prune -a
```

### Ошибка подключения к Go сервисам

```bash
# Вход в API контейнер
docker-compose exec api bash

# Проверка подключения
ping analyzer
ping simplifier

# Тест endpoints
curl http://analyzer:8080/health
curl http://simplifier:8081/health
```

## 📦 Развёртывание на VPS

Полная инструкция в [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)

### Кратко:

1. Установите Docker и Docker Compose на сервер
2. Скопируйте проект на сервер
3. Настройте `.env` (измените `JWT_SECRET_KEY`, используйте PostgreSQL)
4. Создайте systemd сервис
5. Настройте Nginx и SSL

## ✅ Итог

Теперь все 3 сервиса работают в Docker контейнерах:
- ✅ **API** (Python FastAPI) - порт 8000
- ✅ **Analyzer** (Go) - порт 8080
- ✅ **Simplifier** (Go) - порт 8081

**Расширение** обновлено и вызывает упрощение текста.

**На VPS с Linux** всё будет работать идеально через systemd или Docker Compose.
