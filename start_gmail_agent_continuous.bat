@echo off
title Gmail Agent — CONTINUOUS MODE
color 0E

echo.
echo  ==========================================
echo   🤖  GMAIL AUTONOMOUS AGENT
echo   Digital FTE — Gold Tier (Always-On)
echo  ==========================================
echo.
echo  Account : aishaasiddiqui7@gmail.com
echo  Vault   : AI_Employee_Vault\
echo  Mode    : Continuous Polling (checks every 60s)
echo.
echo  [INFO] Starting agent...
echo  [INFO] Press Ctrl+C to stop gracefully.
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

:: Run agent with continuous flag
python gmail_agent.py --continuous

echo.
echo  [DONE] Gmail Agent stopped. Check logs:
echo    - AI_Employee_Vault\Logs\Gmail_Log.md
echo    - AI_Employee_Vault\Audit\Email_Summary_%%DATE:~-4%%-%%DATE:~4,2%%-%%DATE:~7,2%%.md
echo.
pause
