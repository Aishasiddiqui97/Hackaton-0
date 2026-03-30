@echo off
REM Twitter Browser Automation - Live Posting Test
REM WARNING: This will post a REAL tweet to your account

echo ============================================================
echo   Twitter Browser Automation - Live Posting Test
echo ============================================================
echo.
echo WARNING: This will post a REAL tweet to your Twitter account!
echo.
echo Make sure you have:
echo   1. Added TWITTER_EMAIL to .env
echo   2. Added TWITTER_PASSWORD to .env
echo   3. Disabled 2FA or using app password
echo.

set /p confirm="Continue with live posting test? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo.
    echo [INFO] Test cancelled by user
    pause
    exit /b 0
)

echo.
echo [INFO] Activating virtual environment...
call AI_Employee_Vault\venv\Scripts\activate.bat

echo [INFO] Starting live posting test...
echo [INFO] This may take 2-3 minutes...
echo.

python scripts\test_twitter_post.py

if errorlevel 1 (
    echo.
    echo [ERROR] Posting failed. Check logs\twitter_browser_actions.log
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Test Complete
echo ============================================================
echo.
echo Check:
echo   - AI_Employee_Vault\Logs\Twitter_Log.md for activity log
echo   - logs\twitter_browser_actions.log for technical details
echo   - Your Twitter profile for the posted tweet
echo.

pause
