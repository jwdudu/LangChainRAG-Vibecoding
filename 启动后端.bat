@echo off
cd /d "%~dp0backend"
echo ============================================
echo  [RAG] Starting backend on http://127.0.0.1:8000
echo        Press Ctrl+C to stop.
echo ============================================
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
pause
