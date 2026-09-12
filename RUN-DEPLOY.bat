@echo off
REM SANTINEL Automated Deployment
REM Run from: F:\Proiecte AI\santinel
REM Command: RUN-DEPLOY.bat

setlocal enabledelayedexpansion

cd /d "F:\Proiecte AI\santinel"

echo.
echo ============================================================
echo SANTINEL AUTOMATED DEPLOYMENT - All Phases
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    exit /b 1
)

echo [*] Running deployment script...
python DEPLOY-ALL-PHASES.py

if errorlevel 1 (
    echo [ERROR] Deployment failed
    exit /b 1
)

echo.
echo [OK] DEPLOYMENT COMPLETE
echo.
pause
