# Dockerfile для Chinese Text Simplifier API
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Устанавливаем зависимости
RUN apk add --no-cache git ca-certificates

# Копируем go.mod и go.sum
COPY go.mod go.sum ./
RUN go mod download

# Копируем исходный код
COPY . .

# Компилируем
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o simplifier .

# Финальный образ
FROM alpine:latest

WORKDIR /app

# Устанавливаем CA сертификаты
RUN apk --no-cache add ca-certificates

# Копируем скомпилированный бинарник
COPY --from=builder /app/simplifier .

# Создаём директорию для данных
RUN mkdir -p data/cache

# Копируем данные (опционально, можно использовать volumes)
# COPY data/ ./data/

# Экспонируем порт
EXPOSE 8081

# Переменные окружения
ENV PORT=8081
ENV DATA_DIR=/app/data
ENV LOG_LEVEL=info

# Запуск от не-root пользователя (безопасность)
RUN adduser -D -g '' appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8081/health || exit 1

# Команда запуска
CMD ["./simplifier"]
