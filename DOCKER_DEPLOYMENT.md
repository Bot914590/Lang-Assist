# Language Assist - Docker Развёртывание

Этот документ описывает как запустить Language Assist используя Docker.

## 📋 Требования

- Docker (версия 20.10+)
- Docker Compose (версия 2.0+)
- 2GB+ RAM
- 10GB+ свободного места на диске

## 🚀 Быстрый старт (локальная разработка)

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Language_assist
```

### 2. Настройка переменных окружения

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте .env и установите JWT_SECRET_KEY
# Для продакшена используйте надёжный генератор паролей!
```

### 3. Запуск всех сервисов

```bash
# Сборка и запуск
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### 4. Проверка статуса

```bash
# Просмотр логов
docker-compose logs -f

# Проверка работающих контейнеров
docker-compose ps
```

### 5. Доступ к сервисам

| Сервис | URL | Описание |
|--------|-----|----------|
| API | http://localhost:8000 | FastAPI бэкенд |
| Analyzer | http://localhost:8080 | Go токенизатор |
| Simplifier | http://localhost:8081 | Go упроститель |
| Docs | http://localhost:8000/docs | Swagger документация |

### 6. Тестирование

```bash
# Проверка API
curl http://localhost:8000/health

# Проверка Analyzer
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"你好世界","lang":"zh","user_level":1}'

# Проверка Simplifier
curl -X POST http://localhost:8081/simplify \
  -H "Content-Type: application/json" \
  -d '{"text":"美丽","lang":"zh","target_level":2}'
```

## 🛑 Остановка сервисов

```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить тома (база данных будет удалена!)
docker-compose down -v
```

## 📦 Развёртывание на VPS (продакшен)

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### 2. Настройка проекта

```bash
# Клонирование репозитория
git clone <repository-url> /var/www/language-assist
cd /var/www/language-assist

# Создание .env файла
cp .env.example .env

# Редактирование .env
nano .env
```

**Важные изменения для продакшена:**

```env
# База данных (используйте PostgreSQL)
DATABASE_URL=postgresql://user:password@db:5432/langdb

# JWT Secret (обязательно измените!)
JWT_SECRET_KEY=super-secret-key-generated-with-openssl-rand-base64-32

# Go сервисы
GO_ANALYZER_URL=http://analyzer:8080
GO_SIMPLIFIER_URL=http://simplifier:8081
```

### 3. Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/language-assist.service
```

**Содержимое файла:**

```ini
[Unit]
Description=Language Assist Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/language-assist
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

**Активация:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable language-assist
sudo systemctl start language-assist
sudo systemctl status language-assist
```

### 4. Настройка Nginx (опционально)

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/language-assist
```

**Конфигурация Nginx:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Активация:**

```bash
sudo ln -s /etc/nginx/sites-available/language-assist /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Настройка SSL (рекомендуется)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo systemctl enable certbot.timer
```

## 🔧 Управление сервисами

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f api
docker-compose logs -f analyzer
docker-compose logs -f simplifier

# Последние 100 строк
docker-compose logs --tail=100 api
```

### Перезапуск сервисов

```bash
# Перезапуск всех
docker-compose restart

# Перезапуск конкретного
docker-compose restart api
```

### Обновление

```bash
# Pull новых образов
docker-compose pull

# Пересборка и перезапуск
docker-compose up -d --build
```

### Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Место на диске
docker system df
```

## 🐛 Отладка

### Вход в контейнер

```bash
# API контейнер
docker-compose exec api bash

# Analyzer контейнер
docker-compose exec analyzer sh

# Simplifier контейнер
docker-compose exec simplifier sh
```

### Проверка логов

```bash
# Журнал systemd
sudo journalctl -u language-assist -f

# Docker логи
docker-compose logs -f
```

### Тестирование внутри сети

```bash
# Вход в API контейнер
docker-compose exec api bash

# Тест Go сервисов из API
curl http://analyzer:8080/health
curl http://simplifier:8081/health
```

## 📊 Архитектура

```
┌─────────────────┐
│     Nginx       │ (опционально, порт 80/443)
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI (8000) │
│   Python API    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼──────┐
│Analyzer│ │Simplifier│
│(8080)  │ │(8081)   │
│  Go   │ │   Go    │
└───────┘ └─────────┘
```

## 🔐 Безопасность

1. **Измените JWT_SECRET_KEY** в .env
2. **Используйте PostgreSQL** вместо SQLite для продакшена
3. **Настройте firewall** (откройте только 80, 443, 22)
4. **Обновляйте зависимости** регулярно
5. **Используйте HTTPS** для продакшена

## 📝 Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL базы данных | `sqlite:///./user.db` |
| `GO_ANALYZER_URL` | URL Go Analyzer | `http://analyzer:8080` |
| `GO_SIMPLIFIER_URL` | URL Go Simplifier | `http://simplifier:8081` |
| `JWT_SECRET_KEY` | Секретный ключ JWT | `your-secret-key...` |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `1440` |
| `DB_ECHO` | Логирование SQL | `false` |
| `PORT` | Порт Go сервиса | `8080` / `8081` |

## 🆘 Решение проблем

### Контейнер не запускается

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
# Проверка сети
docker-compose exec api ping analyzer
docker-compose exec api ping simplifier

# Проверка портов
docker-compose exec api curl http://analyzer:8080/health
docker-compose exec api curl http://simplifier:8081/health
```

### База данных не сохраняется

```bash
# Проверка томов
docker volume ls

# Проверка прав доступа
ls -la ./data
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус: `docker-compose ps`
3. Проверьте логи systemd: `sudo journalctl -u language-assist`
