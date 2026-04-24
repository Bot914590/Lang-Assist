#!/bin/bash

# Chinese Text Simplifier API - Script для быстрой проверки
# Использование: ./check.sh

set -e

echo "=========================================="
echo "Chinese Text Simplifier API - Проверка"
echo "=========================================="
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Счётчики
PASSED=0
FAILED=0
WARNINGS=0

# Функция для проверки файла
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Файл $1 существует"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Файл $1 отсутствует"
        ((FAILED++))
    fi
}

# Функция для проверки директории
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} Директория $1 существует"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Директория $1 отсутствует"
        ((FAILED++))
    fi
}

# Функция для предупреждения
warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "1. Проверка структуры проекта..."
echo "-------------------------------------------"
check_file "main.go"
check_file "embeddings.go"
check_file "auth.go"
check_file "rate_limit.go"
check_file "errors.go"
check_file "go.mod"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file ".env.example"
check_file ".gitignore"
check_file ".dockerignore"
check_file "LICENSE"
check_file "README.md"
check_file "DEPLOYMENT.md"
check_file "openapi.yaml"
check_file "API_LAYER_CHECKLIST.md"
echo ""

echo "2. Проверка директорий..."
echo "-------------------------------------------"
check_dir "data"
check_dir "tests"
check_dir ".github/workflows"
echo ""

echo "3. Проверка данных..."
echo "-------------------------------------------"
if [ -f "data/hsk.json" ]; then
    SIZE=$(stat -f%z "data/hsk.json" 2>/dev/null || stat -c%s "data/hsk.json" 2>/dev/null || echo "0")
    if [ "$SIZE" -gt 1000000 ]; then
        echo -e "${GREEN}✓${NC} HSK словарь присутствует ($(numfmt --to=iec $SIZE 2>/dev/null || echo "${SIZE} bytes"))"
    else
        warn "HSK словарь слишком маленький, возможно повреждён"
    fi
    ((PASSED++))
else
    echo -e "${RED}✗${NC} HSK словарь отсутствует (data/hsk.json)"
    ((FAILED++))
fi

if [ -f "data/light_Tencent_AILab_ChineseEmbedding.bin" ]; then
    echo -e "${GREEN}✓${NC} Эмбеддинги присутствуют"
    ((PASSED++))
else
    warn "Эмбеддинги отсутствуют (будет работать в режиме без эмбеддингов)"
fi
echo ""

echo "4. Проверка Go модуля..."
echo "-------------------------------------------"
if command -v go &> /dev/null; then
    GO_VERSION=$(go version | cut -d' ' -f3)
    echo -e "${GREEN}✓${NC} Go установлен: $GO_VERSION"
    
    # Проверка go.mod
    if grep -q "go 1.21" go.mod; then
        echo -e "${GREEN}✓${NC} Версия Go в go.mod корректна"
        ((PASSED++))
    else
        warn "Версия Go в go.mod отличается от 1.21"
    fi
    
    # Проверка синтаксиса
    echo "Проверка синтаксиса Go..."
    if go build -o /dev/null . 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Go код компилируется успешно"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} Ошибка компиляции Go кода"
        ((FAILED++))
    fi
else
    warn "Go не установлен, пропускаем проверку"
fi
echo ""

echo "5. Проверка Docker..."
echo "-------------------------------------------"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker установлен"
    ((PASSED++))
    
    # Проверка Dockerfile
    if grep -q "FROM golang:1.21" Dockerfile; then
        echo -e "${GREEN}✓${NC} Dockerfile корректен"
        ((PASSED++))
    else
        warn "Dockerfile использует другую версию Go"
    fi
else
    warn "Docker не установлен, пропускаем проверку"
fi
echo ""

echo "6. Проверка документации..."
echo "-------------------------------------------"
# Проверка README
if grep -q "API Endpoints" README.md; then
    echo -e "${GREEN}✓${NC} README содержит документацию API"
    ((PASSED++))
else
    warn "README может быть неполным"
fi

# Проверка OpenAPI
if grep -q "openapi: 3.0.0" openapi.yaml; then
    echo -e "${GREEN}✓${NC} OpenAPI спецификация корректна"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} OpenAPI спецификация отсутствует или некорректна"
    ((FAILED++))
fi
echo ""

echo "7. Проверка тестов..."
echo "-------------------------------------------"
if [ -f "tests/main_test.go" ]; then
    echo -e "${GREEN}✓${NC} Тесты присутствуют"
    ((PASSED++))
    
    if command -v go &> /dev/null; then
        echo "Запуск тестов..."
        if go test -v ./tests/... 2>&1 | head -20; then
            echo -e "${GREEN}✓${NC} Тесты прошли успешно"
            ((PASSED++))
        else
            warn "Некоторые тесты не прошли"
        fi
    fi
else
    echo -e "${RED}✗${NC} Тесты отсутствуют"
    ((FAILED++))
fi
echo ""

echo "8. Проверка CI/CD..."
echo "-------------------------------------------"
check_file ".github/workflows/go.yml"
check_file ".github/workflows/release.yml"
echo ""

echo "=========================================="
echo "Итоги проверки"
echo "=========================================="
echo -e "${GREEN}Прошло:${NC} $PASSED"
echo -e "${RED}Не прошло:${NC} $FAILED"
echo -e "${YELLOW}Предупреждений:${NC} $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Все проверки пройдены! Проект готов к развёртыванию.${NC}"
    exit 0
else
    echo -e "${RED}✗ Некоторые проверки не пройдены. Исправьте ошибки перед развёртыванием.${NC}"
    exit 1
fi
