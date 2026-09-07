@echo off
setlocal enabledelayedexpansion

cd /d "F:\Proiecte AI\santinel"

(
echo === GIT FIX STARTED ===
echo %date% %time%
echo.

echo Removing .cache from git staging...
git rm --cached -r .cache
echo Exit code: !ERRORLEVEL!
echo.

echo Updating .gitignore...
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
echo .gitignore updated
echo.

echo Staging .gitignore...
git add .gitignore
echo Exit code: !ERRORLEVEL!
echo.

echo Creating commit...
git commit -m "Remove large cache files from git, add .cache to .gitignore"
echo Exit code: !ERRORLEVEL!
echo.

echo Pushing to GitHub...
git push origin main
echo Exit code: !ERRORLEVEL!
echo.

echo === GIT FIX COMPLETED ===
echo %date% %time%
) > git_output.log

echo Fix completed. Check git_output.log for details.
timeout /t 3
