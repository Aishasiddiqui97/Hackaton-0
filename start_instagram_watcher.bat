@echo off
REM Instagram Watcher - PM2 Setup Script (Windows)
REM Starts the Instagram watcher as a permanent background process

echo ==========================================
echo Instagram Watcher - PM2 Setup
echo ==========================================

REM Check if PM2 is installed
where pm2 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PM2 is not installed
    echo.
    echo Install PM2 with:
    echo   npm install -g pm2
    echo   npm install -g pm2-windows-startup
    echo   pm2-startup install
    echo.
    pause
    exit /b 1
)

echo ✅ PM2 is installed

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed
    pause
    exit /b 1
)

echo ✅ Python is available

REM Check if watcher file exists
if not exist "watchers\instagram_watcher.py" (
    echo ❌ Instagram watcher not found at: watchers\instagram_watcher.py
    pause
    exit /b 1
)

echo ✅ Instagram watcher found

REM Stop existing instance if running
echo.
echo Stopping any existing instagram_watcher process...
pm2 stop instagram_watcher 2>nul
pm2 delete instagram_watcher 2>nul

REM Start the watcher
echo.
echo Starting Instagram watcher with PM2...
pm2 start watchers\instagram_watcher.py --name instagram_watcher --interpreter python --max-memory-restart 500M --restart-delay 3000 --exp-backoff-restart-delay 100

REM Save PM2 configuration
echo.
echo Saving PM2 configuration...
pm2 save

echo.
echo ==========================================
echo ✅ Instagram Watcher Started Successfully
echo ==========================================
echo.
echo Useful PM2 Commands:
echo.
echo   View logs:        pm2 logs instagram_watcher
echo   View status:      pm2 status
echo   Restart:          pm2 restart instagram_watcher
echo   Stop:             pm2 stop instagram_watcher
echo   Monitor:          pm2 monit
echo.
echo The watcher will:
echo   - Check Instagram every 5 minutes
echo   - Auto-restart on crash
echo   - Survive system reboot (if pm2-startup is configured)
echo   - Log to AI_Employee_Vault\Logs\instagram_watcher.log
echo.
echo To enable auto-start on Windows reboot:
echo   npm install -g pm2-windows-startup
echo   pm2-startup install
echo.
pause
