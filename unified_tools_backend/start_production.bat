@echo off
echo ===================================================
echo   Sankalp Insight Node - Production Launcher
echo ===================================================
echo.

echo [1/3] Checking Environment...
if not exist ".env" (
    echo [WARN] .env file not found. Creating default...
    echo PORT=8001 > .env
    echo NODE_ENV=production >> .env
)

echo [2/3] Validating Dependencies...
pip install -r requirements.txt > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [3/3] Starting Uvicorn Server...
echo.
echo   - Host: 0.0.0.0
echo   - Port: 8001
echo   - Workers: 1 (Single Process for Determinism)
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1

pause
