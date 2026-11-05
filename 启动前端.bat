@echo off
cd /d "%~dp0frontend"
echo ============================================
echo  [RAG] Starting frontend on http://localhost:5173
echo        Press Ctrl+C to stop.
echo ============================================
npm run dev
pause
