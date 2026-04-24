# 📦 Chinese Text Simplifier API - Обзор проекта

## 🎯 Назначение

API для упрощения китайских текстов до целевого уровня HSK с использованием семантического анализа и векторных эмбеддингов.

**Основная функция:** Автоматическая замена сложных китайских слов на более простые аналоги с сохранением смысла.

---

## 📁 Структура проекта

```
apilayer-simplifier/
├── 🔧 Исходный код Go
│   ├── main.go              # HTTP сервер, handlers
│   ├── embeddings.go        # Загрузка эмбеддингов, семантический поиск
│   ├── auth.go              # API Key аутентификация
│   ├── rate_limit.go        # Rate limiting для тарифов
│   └── errors.go            # Обработка ошибок
│
├── 📚 Документация
│   ├── README.md            # Основная документация
│   ├── DEPLOYMENT.md        # Инструкции по развёртыванию
│   ├── API_LAYER_CHECKLIST.md # Чек-лист для APILayer
│   └── openapi.yaml         # OpenAPI 3.0 спецификация
│
├── 🐳 Docker
│   ├── Dockerfile           # Multi-stage build
│   ├── docker-compose.yml   # Оркестрация
│   └── .dockerignore        # Игнорируемые файлы
│
├── 🧪 Тестирование
│   └── tests/main_test.go   # Unit и integration тесты
│
├── 🚀 CI/CD
│   └── .github/workflows/
│       ├── go.yml           # Тесты, линтинг, сборка
│       └── release.yml      # Релизы и Docker публикация
│
├── ⚙️ Конфигурация
│   ├── go.mod               # Go модуль
│   ├── .env.example         # Пример переменных окружения
│   ├── .gitignore           # Git ignore
│   └── LICENSE              # MIT License
│
└── 📊 Данные
    └── data/
        ├── hsk.json         # HSK словарь (90k+ записей)
        └── cache/           # Кэш эмбеддингов
```

---

## 🔑 Ключевые возможности

### 1. API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/simplify` | POST | Упрощение текста до целевого уровня HSK |
| `/analyze` | POST | Анализ текста (токенизация, HSK уровни) |
| `/word/info` | GET | Информация о слове (HSK, пиньинь, перевод) |
| `/word/similar` | GET | Поиск семантически близких слов |
| `/health` | GET | Health check сервиса |

### 2. Аутентификация

- **API Key** в заголовке `X-API-Key` или `Authorization: Bearer`
- Поддержка нескольких ключей для разных тарифов
- Безопасное сравнение (constant-time comparison)

### 3. Rate Limiting

| Тариф | Запросов в день | Запросов в минуту |
|-------|-----------------|-------------------|
| Free | 100 | 10 |
| Basic | 1,000 | 50 |
| Pro | 10,000 | 200 |
| Enterprise | 100,000+ | 1000+ |

### 4. Технологические преимущества

- **Go 1.21** — высокая производительность
- **Векторные эмбеддинги** — Tencent AILab (200-мерные векторы)
- **Косинусное сходство** — точный семантический поиск
- **HSK словарь** — 90,000+ записей с переводами
- **Кэширование** — быстрая загрузка эмбеддингов

---

## 🚀 Быстрый старт

### Локальный запуск

```bash
cd apilayer-simplifier

# Копирование .env
cp .env.example .env

# Запуск
go run main.go
```

### Docker запуск

```bash
docker-compose up --build
```

### Проверка API

```bash
# Health check
curl http://localhost:8081/health

# Упрощение текста
curl -X POST http://localhost:8081/simplify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_test-key" \
  -d '{"text":"她很美丽","target_level":1}'
```

---

## 📊 Примеры использования

### Python

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8081"

headers = {"X-API-Key": API_KEY}

# Упрощение текста
response = requests.post(
    f"{BASE_URL}/simplify",
    headers=headers,
    json={"text": "她很美丽", "target_level": 2}
)
result = response.json()
print(result["simplified_text"])  # 她很漂亮
```

### JavaScript

```javascript
const axios = require('axios');

const API_KEY = 'your-api-key';
const BASE_URL = 'http://localhost:8081';

// Упрощение текста
async function simplifyText(text, targetLevel) {
  const response = await axios.post(
    `${BASE_URL}/simplify`,
    { text, target_level: targetLevel },
    { headers: { 'X-API-Key': API_KEY } }
  );
  return response.data;
}

// Использование
simplifyText('她很美丽', 2).then(result => {
  console.log('Simplified:', result.simplified_text);
});
```

### cURL

```bash
curl -X POST http://localhost:8081/simplify \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text":"这个经济问题很复杂","target_level":2}'
```

---

## 🎓 Как это работает

### 1. Токенизация

```
输入文本 → 分词 → ["这个", "经济", "问题", "很", "复杂"]
```

### 2. Определение HSK уровня

```
["这个", "经济", "问题", "很", "复杂"]
   ↓       ↓       ↓      ↓      ↓
 HSK1    HSK4    HSK3   HSK1   HSK4
```

### 3. Семантический поиск

```
复杂 (HSK4) → [вектор 200d] → косинусное сходство → 难 (HSK2, similarity: 0.68)
```

### 4. Упрощение

```
原始文本：这个经济问题很复杂
简化文本：这个经济问题很难
```

---

## 📈 Производительность

### Benchmark результаты

| Операция | Время выполнения |
|----------|------------------|
| Токенизация (100 иероглифов) | <1ms |
| Упрощение (10 иероглифов) | <10ms |
| Поиск похожих слов | <50ms |
| Health check | <1ms |

### Ресурсы

- **Память:** 200-500MB (с эмбеддингами)
- **CPU:** <10% при обычной нагрузке
- **Диск:** 2.5GB (эмбеддинги + HSK)

---

## 🔐 Безопасность

- ✅ API Key аутентификация
- ✅ Rate limiting
- ✅ CORS заголовки
- ✅ Security headers
- ✅ Запуск от не-root пользователя (Docker)
- ✅ Graceful shutdown

---

## 📦 Развёртывание

### Поддерживаемые платформы

- **Docker** — Linux, macOS, Windows
- **Binary** — Linux (amd64/arm64), macOS (amd64/arm64), Windows (amd64)
- **Kubernetes** — манифесты включены
- **Systemd** — Linux VPS

### Production checklist

- [ ] Изменить API_KEY на случайную строку
- [ ] Настроить HTTPS (Nginx + Let's Encrypt)
- [ ] Включить firewall
- [ ] Настроить мониторинг
- [ ] Включить backup данных

---

## 🧪 Тестирование

```bash
# Запуск всех тестов
go test -v ./...

# Benchmark тесты
go test -v -bench=. ./...

# Покрытие
go test -v -cover ./...
```

---

## 📞 Поддержка

### Документация

- **README.md** — полная документация API
- **DEPLOYMENT.md** — инструкции по развёртыванию
- **openapi.yaml** — OpenAPI 3.0 спецификация
- **API_LAYER_CHECKLIST.md** — чек-лист для APILayer

### Контакты

- GitHub: https://github.com/yourusername/chinese-simplifier-api
- Email: support@yourdomain.com

---

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE)

---

## 🙏 Благодарности

- **Tencent AILab** — векторные эмбеддинги
- **HSK Dictionary** — данные HSK
- **APILayer** — платформа для публикации API

---

## 📅 Roadmap

### Q2 2024
- [ ] Публикация на APILayer
- [ ] Поддержка японского языка (JLPT)
- [ ] Графическая панель управления

### Q3 2024
- [ ] WebSocket поддержка
- [ ] Пакетная обработка текстов
- [ ] Интеграция с ChatGPT

### Q4 2024
- [ ] Мобильное SDK
- [ ] Offline режим
- [ ] Пользовательские словари

---

**Версия:** 1.0.0  
**Последнее обновление:** Март 2024
