@echo off
echo 🕳️ Starting Blackhole Infiverse LLP Backend...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Trying 'py' command...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python not found! Please install Python 3.8+
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo ✅ Python found: %PYTHON_CMD%
echo.

echo 📦 Installing required packages...
%PYTHON_CMD% -m pip install fastapi uvicorn requests beautifulsoup4 pandas numpy httpx python-dotenv pydantic

echo.
echo 🚀 Starting server...
echo 🌐 Server will be at: http://localhost:8000
echo 📚 API docs will be at: http://localhost:8000/docs
echo.
echo ⏹️ Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
