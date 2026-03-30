@echo off
title Gmail Agent Dashboard — localhost:5050
color 0B

echo.
echo  ==========================================
echo   🌐  GMAIL AGENT DASHBOARD
echo   Digital FTE — Gold Tier
echo   http://localhost:5050
echo  ==========================================
echo.
echo  [INFO] Starting web dashboard...
echo  [INFO] Press Ctrl+C to stop.
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

:: Install Flask if not present
python -c "import flask" 2>nul || (
    echo [INFO] Installing Flask...
    pip install flask --quiet
)

:: Open browser after 2 second delay
start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:5050"

:: Run dashboard
python gmail_dashboard.py

pause
