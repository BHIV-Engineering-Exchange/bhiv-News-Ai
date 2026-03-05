@echo off
echo Starting Noopur News AI Platform (Full Stack)...
echo.

REM 1. Start Sankalp Tools (Legacy Backend) on 8001
echo [1/4] Starting Sankalp Tools (Port 8001)...
start "Sankalp Tools (8001)" cmd /k "cd Task2-master\unified_tools_backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001"

REM 2. Start Noopur Core (Node.js) on 3001
echo [2/4] Starting Noopur Core (Port 3001)...
start "Noopur Core (3001)" cmd /k "cd news-ai-final-main && npm run dev"

REM 3. Start Noopur Gateway (FastAPI) on 8000
echo [3/4] Starting Noopur Gateway (Port 8000)...
start "Noopur Gateway (8000)" cmd /k "cd news-ai-final-main\fastapi_microservices && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM 4. Start Chandragupta Frontend (Next.js) on 3002
echo [4/4] Starting Chandragupta Frontend (Port 3002)...
start "Chandragupta Frontend (3002)" cmd /k "cd Task2-master\blackhole-frontend && npm run dev"

echo.
echo ✅ Services starting...
echo Gateway: http://localhost:8000
echo Core: http://localhost:3001
echo Tools: http://localhost:8001
echo Frontend: http://localhost:3002
echo.
pause
