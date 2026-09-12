@echo off
REM SANTINEL DEPLOYMENT SCRIPT
REM This script fixes the git blocker and deploys to Vercel

setlocal enabledelayedexpansion
cd /d "F:\Proiecte AI\santinel"

echo ================================
echo SANTINEL DEPLOYMENT SCRIPT
echo ================================
echo.

REM Step 1: Check for BFG
echo [1/6] Checking for BFG Repo-Cleaner...
if not exist "F:\Tools\bfg-1.14.0.jar" (
    echo      Downloading BFG...
    if not exist "F:\Tools" mkdir "F:\Tools"
    powershell -Command "Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar' -OutFile 'F:\Tools\bfg-1.14.0.jar'"
    if errorlevel 1 (
        echo      FAIL: Could not download BFG
        exit /b 1
    )
    echo      OK: BFG downloaded
) else (
    echo      OK: BFG already present
)

REM Step 2: Navigate to repo
echo [2/6] Navigating to santinel repository...
if not exist "F:\Proiecte AI\santinel\.git" (
    echo      FAIL: Repository not found
    exit /b 1
)
cd /d "F:\Proiecte AI\santinel"
echo      OK: In repository
echo.

REM Step 3: Run BFG
echo [3/6] Running BFG to remove 138.49 MB blob...
java -jar "F:\Tools\bfg-1.14.0.jar" --delete-files d01c3014881c9c6f3133c182f3d2887eb6ca1c789a7538c5c007196857a0a6a9
if errorlevel 1 (
    echo      FAIL: BFG failed
    exit /b 1
)
echo      OK: BFG completed
echo.

REM Step 4: Expire reflog
echo [4/6] Cleaning git reflog...
git reflog expire --expire=now --all
if errorlevel 1 (
    echo      FAIL: git reflog failed
    exit /b 1
)
echo      OK: Reflog expired
echo.

REM Step 5: Garbage collection
echo [5/6] Running garbage collection (1-2 minutes)...
git gc --prune=now --aggressive
if errorlevel 1 (
    echo      FAIL: git gc failed
    exit /b 1
)
echo      OK: Garbage collection complete
echo.

REM Step 6: Push to GitHub
echo [6/6] Pushing to GitHub (force push)...
git push origin main --force
if errorlevel 1 (
    echo      FAIL: Push failed
    exit /b 1
)

echo.
echo ================================
echo SUCCESS! Vercel will deploy in 2-3 minutes
echo ================================
echo.
echo Next steps:
echo 1. Watch: https://vercel.com/dashboard
echo 2. Look for green DEPLOYMENT SUCCESSFUL
echo 3. Your live URL: https://santinel-XXXXX.vercel.app
echo.
pause
