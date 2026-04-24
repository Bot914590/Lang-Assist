@echo off
REM Chinese Text Simplifier API - Script для быстрой проверки (Windows)
REM Использование: check.bat

setlocal enabledelayedexpansion

echo ==========================================
echo Chinese Text Simplifier API - Проверка
echo ==========================================
echo.

REM Счётчики
set PASSED=0
set FAILED=0
set WARNINGS=0

REM Функция для проверки файла
:check_file
if exist "%~1" (
    echo [OK] Файл %~1 существует
    set /a PASSED+=1
) else (
    echo [FAIL] Файл %~1 отсутствует
    set /a FAILED+=1
)
goto :eof

REM Функция для проверки директории
:check_dir
if exist "%~1\" (
    echo [OK] Директория %~1 существует
    set /a PASSED+=1
) else (
    echo [FAIL] Директория %~1 отсутствует
    set /a FAILED+=1
)
goto :eof

echo 1. Проверка структуры проекта...
echo -------------------------------------------
call :check_file "main.go"
call :check_file "embeddings.go"
call :check_file "auth.go"
call :check_file "rate_limit.go"
call :check_file "errors.go"
call :check_file "go.mod"
call :check_file "Dockerfile"
call :check_file "docker-compose.yml"
call :check_file ".env.example"
call :check_file ".gitignore"
call :check_file "LICENSE"
call :check_file "README.md"
call :check_file "DEPLOYMENT.md"
call :check_file "openapi.yaml"
call :check_file "API_LAYER_CHECKLIST.md"
echo.

echo 2. Проверка директорий...
echo -------------------------------------------
call :check_dir "data"
call :check_dir "tests"
if exist ".github\workflows\" (
    echo [OK] Директория .github\workflows существует
    set /a PASSED+=1
) else (
    echo [FAIL] Директория .github\workflows отсутствует
    set /a FAILED+=1
)
echo.

echo 3. Проверка данных...
echo -------------------------------------------
if exist "data\hsk.json" (
    for %%A in ("data\hsk.json") do set SIZE=%%~zA
    if !SIZE! GTR 1000000 (
        echo [OK] HSK словарь присутствует
        set /a PASSED+=1
    ) else (
        echo [WARN] HSK словарь слишком маленький
        set /a WARNINGS+=1
    )
) else (
    echo [FAIL] HSK словарь отсутствует
    set /a FAILED+=1
)

if exist "data\light_Tencent_AILab_ChineseEmbedding.bin" (
    echo [OK] Эмбеддинги присутствуют
    set /a PASSED+=1
) else (
    echo [WARN] Эмбеддинги отсутствуют
    set /a WARNINGS+=1
)
echo.

echo 4. Проверка Go модуля...
echo -------------------------------------------
where go >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Go установлен
    set /a PASSED+=1
    
    REM Проверка go.mod
    findstr /c:"go 1.21" go.mod >nul
    if %errorlevel% equ 0 (
        echo [OK] Версия Go в go.mod корректна
        set /a PASSED+=1
    ) else (
        echo [WARN] Версия Go в go.mod отличается от 1.21
        set /a WARNINGS+=1
    )
    
    REM Проверка компиляции
    echo Проверка компиляции...
    go build -o NUL . >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Go код компилируется успешно
        set /a PASSED+=1
    ) else (
        echo [FAIL] Ошибка компиляции Go кода
        set /a FAILED+=1
    )
) else (
    echo [WARN] Go не установлен
    set /a WARNINGS+=1
)
echo.

echo 5. Проверка Docker...
echo -------------------------------------------
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker установлен
    set /a PASSED+=1
) else (
    echo [WARN] Docker не установлен
    set /a WARNINGS+=1
)
echo.

echo 6. Проверка документации...
echo -------------------------------------------
findstr /c:"API Endpoints" README.md >nul
if %errorlevel% equ 0 (
    echo [OK] README содержит документацию API
    set /a PASSED+=1
) else (
    echo [WARN] README может быть неполным
    set /a WARNINGS+=1
)

findstr /c:"openapi: 3.0.0" openapi.yaml >nul
if %errorlevel% equ 0 (
    echo [OK] OpenAPI спецификация корректна
    set /a PASSED+=1
) else (
    echo [FAIL] OpenAPI спецификация отсутствует
    set /a FAILED+=1
)
echo.

echo 7. Проверка тестов...
echo -------------------------------------------
if exist "tests\main_test.go" (
    echo [OK] Тесты присутствуют
    set /a PASSED+=1
) else (
    echo [FAIL] Тесты отсутствуют
    set /a FAILED+=1
)
echo.

echo 8. Проверка CI/CD...
echo -------------------------------------------
call :check_file ".github\workflows\go.yml"
call :check_file ".github\workflows\release.yml"
echo.

echo ==========================================
echo Итоги проверки
echo ==========================================
echo Прошло: %PASSED%
echo Не прошло: %FAILED%
echo Предупреждений: %WARNINGS%
echo.

if %FAILED% equ 0 (
    echo [OK] Все проверки пройдены! Проект готов к развёртыванию.
    exit /b 0
) else (
    echo [FAIL] Некоторые проверки не пройдены.
    exit /b 1
)
