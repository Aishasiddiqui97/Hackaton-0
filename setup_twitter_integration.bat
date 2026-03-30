@echo off
REM Complete Twitter/X Integration Setup
echo ========================================
echo Twitter/X Integration - Complete Setup
echo ========================================
echo.

cd /d "%~dp0"

echo [Step 1/4] Installing Node.js dependencies...
call npm install express playwright-extra puppeteer-extra-plugin-stealth speakeasy
if %errorlevel% neq 0 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

echo.
echo [Step 2/4] Installing Playwright Chromium...
call npx playwright install chromium
if %errorlevel% neq 0 (
    echo ERROR: Playwright install failed
    pause
    exit /b 1
)

echo.
echo [Step 3/4] Creating required directories...
if not exist "sessions\twitter" mkdir "sessions\twitter"
if not exist "AI_Employee_Vault\Logs" mkdir "AI_Employee_Vault\Logs"
if not exist "AI_Employee_Vault\Social_Media" mkdir "AI_Employee_Vault\Social_Media"
if not exist "logs" mkdir "logs"

echo.
echo [Step 4/4] Verifying .env configuration...
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.template to .env and configure your credentials.
    echo.
    echo Required variables:
    echo   TWITTER_USERNAME=your_username
    echo   TWITTER_PASSWORD=your_password
    echo   TWITTER_2FA_SECRET=optional
    echo.
) else (
    echo .env file found - please verify credentials are set
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Configure .env with your Twitter credentials
echo 2. Run: start_twitter_mcp.bat (Terminal 1)
echo 3. Run: start_twitter_watcher.bat (Terminal 2)
echo 4. Test: python test_twitter_integration.py
echo.
echo Documentation:
echo - TWITTER_SETUP_COMPLETE.md (full guide)
echo - TWITTER_QUICK_REFERENCE.md (quick commands)
echo.
pause
