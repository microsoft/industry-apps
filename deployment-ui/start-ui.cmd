@echo off
REM Simple launcher for Deployment UI using cmd.exe
REM No PowerShell execution policy issues

echo Starting Module Deployment UI...
echo.

REM Start backend in new window
echo Starting backend server...
start "Deployment UI - Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak >nul

REM Start frontend in current window
echo Starting frontend server...
echo.
echo =============================================
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo =============================================
echo.
echo Press Ctrl+C to stop the frontend
echo.

cd frontend
npm run dev
