@echo off
REM Быстрый старт Language Assist с Docker

echo ==================================
echo Language Assist - Быстрый старт
echo ==================================

REM Проверка Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker ne ustanovlen!
    echo Ustanovite Docker: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker Compose ne ustanovlen!
    echo Ustanovite Docker Compose: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo [OK] Docker i Docker Compose naideny

REM Sozdanie .env esli net
if not exist .env (
    echo Sozdanie .env faila...
    copy .env.example .env
    echo Izmenite JWT_SECRET_KEY v faile .env dlya produkshena!
)

REM Zapusk servisov
echo Sbornka i zapusk servisov...
docker-compose up -d --build

REM Ozhidanie zapuska
echo Ozhidanie zapuska servisov...
timeout /t 10 /nobreak >nul

REM Proverka statusa
echo Status servisov:
docker-compose ps

REM Testirovanie
echo.
echo Testirovanie servisov...

echo 1. Test API...
curl -s http://localhost:8000/health >nul 2>&1 && echo [OK] API rabotaet || echo [ERROR] API ne otvechaet

echo 2. Test Analyzer...
curl -s http://localhost:8080/health >nul 2>&1 && echo [OK] Analyzer rabotaet || echo [ERROR] Analyzer ne otvechaet

echo 3. Test Simplifier...
curl -s http://localhost:8081/health >nul 2>&1 && echo [OK] Simplifier rabotaet || echo [ERROR] Simplifier ne otvechaet

echo.
echo ==================================
echo Language Assist zapushchen!
echo.
echo Servisy dostupny po adresam:
echo    API:       http://localhost:8000
echo    Docs:      http://localhost:8000/docs
echo    Analyzer:  http://localhost:8080
echo    Simplifier: http://localhost:8081
echo.
echo Poleznye komandy:
echo    Prosmotr logov:     docker-compose logs -f
echo    Ostanovka:          docker-compose down
echo    Perezapusk:         docker-compose restart
echo.
pause
