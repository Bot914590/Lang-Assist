#!/bin/bash
# Быстрый старт Language Assist с Docker

echo "🚀 Language Assist - Быстрый старт"
echo "=================================="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создание .env если нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp .env.example .env
    echo "⚠️  Измените JWT_SECRET_KEY в файле .env для продакшена!"
fi

# Запуск сервисов
echo "🔨 Сборка и запуск сервисов..."
docker-compose up -d --build

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo "📊 Статус сервисов:"
docker-compose ps

# Тестирование
echo ""
echo "🧪 Тестирование сервисов..."

echo "1️⃣  Тест API..."
curl -s http://localhost:8000/health && echo " ✅ API работает" || echo " ❌ API не отвечает"

echo "2️⃣  Тест Analyzer..."
curl -s http://localhost:8080/health > /dev/null && echo " ✅ Analyzer работает" || echo " ❌ Analyzer не отвечает"

echo "3️⃣  Тест Simplifier..."
curl -s http://localhost:8081/health > /dev/null && echo " ✅ Simplifier работает" || echo " ❌ Simplifier не отвечает"

echo ""
echo "=================================="
echo "✅ Language Assist запущен!"
echo ""
echo "📍 Сервисы доступны по адресам:"
echo "   API:       http://localhost:8000"
echo "   Docs:      http://localhost:8000/docs"
echo "   Analyzer:  http://localhost:8080"
echo "   Simplifier: http://localhost:8081"
echo ""
echo "📋 Полезные команды:"
echo "   Просмотр логов:     docker-compose logs -f"
echo "   Остановка:          docker-compose down"
echo "   Перезапуск:         docker-compose restart"
echo ""
