@echo off
REM Production startup script for News AI Backend (Windows)
REM This script starts the application using Gunicorn + Uvicorn

echo 🚀 Starting News AI Backend in Production Mode

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found. Please create one based on .env.example
    pause
    exit /b 1
)

REM Load environment variables from .env file
for /f "tokens=*" %%i in (.env) do set %%i

REM Set default values if not set
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production
if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8000
if "%WORKERS%"=="" set WORKERS=4
if "%LOG_LEVEL%"=="" set LOG_LEVEL=INFO

echo 📋 Configuration:
echo    Environment: %ENVIRONMENT%
echo    Host: %HOST%
echo    Port: %PORT%
echo    Workers: %WORKERS%
echo    Log Level: %LOG_LEVEL%

REM Start Gunicorn
echo 🔄 Starting Gunicorn server...
gunicorn --config gunicorn.conf.py app.api.main:app

pause