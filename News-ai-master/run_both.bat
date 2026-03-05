@echo off
echo 🚀 Starting Blackhole Infiverse LLP News AI System
echo.

REM Check if required directories exist
if not exist "blackhole-frontend" (
    echo ❌ Frontend directory not found!
    pause
    exit /b 1
)

if not exist "unified_tools_backend" (
    echo ❌ Backend directory not found!
    pause
    exit /b 1
)

echo 📦 Starting Backend Server...
start "Backend Server" cmd /k "cd unified_tools_backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo 🌐 Starting Frontend Development Server...
start "Frontend Server" cmd /k "cd blackhole-frontend && npm run dev"

echo.
echo ✅ Both servers are starting up!
echo.
echo 🔗 Frontend: http://localhost:3000
echo 🔗 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo ⏹️ Close both command windows to stop the servers
echo.
pause