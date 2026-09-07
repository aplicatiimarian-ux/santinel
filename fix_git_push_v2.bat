@echo off
cd /d "F:\Proiecte AI\santinel"
git rm --cached -r .cache > nul 2>&1
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
git add .gitignore
git commit -m "Remove large cache files from git, add .cache to .gitignore"
git push origin main
