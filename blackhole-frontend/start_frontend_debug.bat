@echo off
echo Starting frontend... > frontend_debug.log
echo Current directory: %CD% >> frontend_debug.log
echo Node version: >> frontend_debug.log
node -v >> frontend_debug.log 2>&1
echo NPM version: >> frontend_debug.log
npm -v >> frontend_debug.log 2>&1
echo Running npm run dev... >> frontend_debug.log
npm run dev >> frontend_debug.log 2>&1
