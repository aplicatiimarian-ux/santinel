@echo off
cd /d "F:\Proiecte AI\santinel"

echo Activating venv...
call venv\Scripts\activate.bat

echo Starting FastAPI backend...
python start_api.py
