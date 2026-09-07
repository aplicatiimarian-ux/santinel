@echo off
setlocal enabledelayedexpansion

REM SANTINEL Dev Server Startup Script
REM Navigare la folder proiect
cd /d "F:\Proiecte AI\santinel"

REM Verifica daca npm e instalat
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: npm not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo ========================================
echo SANTINEL Development Server
echo ========================================
echo.
echo Installing dependencies...
echo.

REM Instaleaza dependencies
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dependencies installed successfully!
echo ========================================
echo.
echo Starting dev server on https://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

REM Porneste dev server
call npm run dev

pause
