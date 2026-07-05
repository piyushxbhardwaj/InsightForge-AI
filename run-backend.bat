@echo off
echo Starting InsightForge AI Backend Server...
cd backend
call .\venv\Scripts\activate
python -m app.main
