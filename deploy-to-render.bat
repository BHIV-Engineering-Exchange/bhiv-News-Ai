@echo off
REM Quick deployment script for Windows
REM This helps you push to GitHub and provides next steps

echo ========================================
echo   News AI - Render Deployment Helper
echo ========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
)

REM Show current status
echo Current Git Status:
echo -------------------
git status
echo.

REM Ask for commit message
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Prepare for Render deployment

echo.
echo Adding all files...
git add .

echo.
echo Committing changes...
git commit -m "%commit_msg%"

echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo.
echo 1. Create a new repository on GitHub
echo    Visit: https://github.com/new
echo.
echo 2. Copy the repository URL (e.g., https://github.com/username/repo.git)
echo.
echo 3. Run these commands:
echo    git remote add origin YOUR_REPO_URL
echo    git push -u origin main
echo.
echo 4. Then deploy on Render:
echo    - Go to https://dashboard.render.com
echo    - Click "New +" -^> "Blueprint"
echo    - Connect your GitHub repo
echo    - Click "Apply"
echo.
echo 5. After deployment, update CORS:
echo    cd unified_tools_backend
echo    python update_cors.py https://YOUR-FRONTEND-URL.onrender.com
echo    git add main.py
echo    git commit -m "Update CORS for production"
echo    git push
echo.
echo ========================================
echo   Documentation:
echo ========================================
echo.
echo - Quick Start: RENDER_QUICKSTART.md
echo - Full Guide: RENDER_DEPLOYMENT.md
echo - Checklist: DEPLOYMENT_CHECKLIST.md
echo - Summary: DEPLOYMENT_SUMMARY.md
echo.
pause
