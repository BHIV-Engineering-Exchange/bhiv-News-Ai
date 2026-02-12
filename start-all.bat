@echo off
echo Starting News AI Platform...
echo.

echo [1/2] Starting Backend (Port 8000)...
start "Backend" cmd /k "cd unified_tools_backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Cleaning frontend cache...
cd blackhole-frontend
if exist .next rmdir /s /q .next
cd ..

echo [2/2] Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd blackhole-frontend && npm run dev"

echo.
echo ✅ Services starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
