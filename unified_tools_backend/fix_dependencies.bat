@echo off
echo 🔧 Fixing Python 3.14 Compatibility Issues...
echo.
echo This script will upgrade dependencies to versions compatible with Python 3.14
echo The main fix: Upgrading OpenAI from 1.3.7 (uses Pydantic V1) to 1.12.0+ (uses Pydantic V2)
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
%PYTHON_CMD% --version
echo.

echo 📦 Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo 📦 Uninstalling old incompatible packages...
%PYTHON_CMD% -m pip uninstall -y openai pydantic fastapi uvicorn

echo.
echo 📦 Installing updated compatible packages from requirements.txt...
%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo ✅ Dependencies updated!
echo.
echo 🚀 You can now start the server with: start_server.bat
echo.
pause

