@echo off
title Gmail Autonomous Agent — Digital FTE Gold Tier
color 0A

echo.
echo  ==========================================
echo   🤖  GMAIL AUTONOMOUS AGENT
echo   Digital FTE — Gold Tier
echo  ==========================================
echo.
echo  Account : %EMAIL_ADDRESS%
echo  Vault   : AI_Employee_Vault\
echo  Mode    : Ralph Wiggum Loop
echo.
echo  [INFO] Starting agent...
echo  [INFO] Press Ctrl+C to stop gracefully.
echo.

cd /d "%~dp0"

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Test connection first
echo [INFO] Verifying Gmail credentials...
python gmail_agent.py --test-connection
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Connection test FAILED.
    echo  [FIX]   Make sure EMAIL_PASSWORD in .env is a Google App Password.
    echo  [LINK]  myaccount.google.com/apppasswords
    echo.
    pause
    exit /b 1
)

echo.
echo  [OK] Connection verified. Starting full agent loop...
echo.

:: Run the full agent
python gmail_agent.py

echo.
echo  [DONE] Gmail Agent stopped. Check logs:
echo    - AI_Employee_Vault\Logs\Gmail_Log.md
echo    - AI_Employee_Vault\Audit\Email_Summary_%date:~-4%-%date:~3,2%-%date:~0,2%.md
echo.
pause
