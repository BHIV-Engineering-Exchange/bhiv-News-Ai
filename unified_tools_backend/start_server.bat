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

echo 📦 Installing required packages from requirements.txt...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo 🚀 Starting server...
echo 🌐 Server will be at: http://localhost:8001
echo 📚 API docs will be at: http://localhost:8001/docs
echo.
echo ⏹️ Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% -m uvicorn main:app --reload --host 0.0.0.0 --port 8001

pause
