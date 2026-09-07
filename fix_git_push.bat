@echo off
setlocal enabledelayedexpansion

REM Navigate to project
cd /d "F:\Proiecte AI\santinel"

echo.
echo ========================================
echo Fixing Git LFS Issue
echo ========================================
echo.

REM Remove .cache from git staging
echo Removing .cache from git staging...
git rm --cached -r .cache
if %errorlevel% neq 0 (
    echo ERROR: Failed to remove .cache from git
    pause
    exit /b 1
)

echo.
echo Updating .gitignore...
REM Update .gitignore to prevent .cache from being tracked
(
echo Claude outputs/
echo *.env
echo .env
echo .env.local
echo .cache/
echo node_modules/
echo __pycache__/
echo .pytest_cache/
echo .coverage
echo venv/
) > .gitignore

REM Stage .gitignore
git add .gitignore

echo.
echo Committing changes...
git commit -m "Remove large cache files from git, add .cache to .gitignore"
if %errorlevel% neq 0 (
    echo ERROR: Failed to commit
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ERROR: Failed to push
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Git push completed
echo ========================================
echo.
pause
