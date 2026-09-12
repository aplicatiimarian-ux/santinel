@echo off
REM Remove .env.txt from entire git history using BFG

cd /d "F:\Proiecte AI\santinel"

echo Removing .env.txt from all commits in history...
java -jar "F:\Tools\bfg-1.14.0.jar" --delete-files .env.txt --no-blob-protection
if errorlevel 1 (
    echo FAIL: BFG could not remove .env.txt
    exit /b 1
)
echo OK: .env.txt removed from history

echo.
echo Cleaning reflog...
git reflog expire --expire=now --all
echo OK: Reflog expired

echo.
echo Running garbage collection...
git gc --prune=now --aggressive
if errorlevel 1 (
    echo FAIL: git gc failed
    exit /b 1
)
echo OK: Garbage collection complete

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
