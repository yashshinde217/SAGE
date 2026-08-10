@echo off
setlocal

echo Starting SAGE (native, air-gapped)...

start "SAGE API" /B cmd /c "cd api && uv run uvicorn main:app --port 8000"

timeout /t 2 /nobreak >nul

echo API starting in background — http://localhost:8000
echo Starting web (Ctrl+C to stop both)...

cd web
call npm run dev

echo.
echo Shutting down SAGE...
taskkill /F /FI "WINDOWTITLE eq SAGE API*" >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1

endlocal