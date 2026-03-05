@echo off
echo Installing dependencies...

echo [1/4] Sankalp Tools...
cd Task2-master\unified_tools_backend
pip install -r requirements.txt
cd ..\..

echo [2/4] Noopur Core...
cd news-ai-final-main
npm install
cd ..

echo [3/4] Noopur Gateway...
cd news-ai-final-main\fastapi_microservices
pip install -r requirements.txt
cd ..\..

echo [4/4] Chandragupta Frontend...
cd Task2-master\blackhole-frontend
npm install
cd ..\..

echo Done!
pause
