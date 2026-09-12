@echo off
cd /d "F:\Proiecte AI\santinel"

echo Activating venv...
call venv\Scripts\activate.bat

echo Starting Vite dev server...
echo.
echo When ready, open: http://localhost:5173
echo.
npm run dev
