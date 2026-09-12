@echo off
REM Remove .env.txt from git and push again

cd /d "F:\Proiecte AI\santinel"

echo Removing .env.txt from git tracking...
git rm --cached .env.txt
if errorlevel 1 (
    echo FAIL: Could not remove .env.txt
    exit /b 1
)
echo OK: .env.txt removed from tracking

echo.
echo Committing removal...
git commit -m "Remove .env.txt containing API keys"
if errorlevel 1 (
    echo FAIL: Could not commit
    exit /b 1
)
echo OK: Committed

echo.
echo Pushing to GitHub...
git push origin main --force
if errorlevel 1 (
    echo FAIL: Push failed
    exit /b 1
)

echo.
echo ================================
echo SUCCESS! Push complete
echo Vercel deploying now...
echo ================================
echo.
pause
