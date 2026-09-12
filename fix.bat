@echo off
cd F:\Proiecte AI\santinel

echo Fixing requirements.txt...

REM Create backup
copy requirements.txt requirements.txt.bak

REM Create fixed requirements.txt
(
echo setuptools^>=68.0
echo fastapi==0.104.1
echo uvicorn==0.24.0
echo python-dotenv==1.0.0
echo pydantic==2.5.0
echo pyjwt==2.14.0
echo httpx==0.25.0
echo sqlalchemy==2.0.23
echo psycopg2-binary==2.9.9
) > requirements.txt

echo Committing...
git add requirements.txt
git commit -m "Fix: Add setuptools, update pyjwt to 2.14.0"
git push origin main

echo DONE - Render redeploying now
pause
