@echo off
REM Twitter Browser Automation - Test Script
REM Tests the Twitter browser automation setup

echo ============================================================
echo   Twitter Browser Automation - Setup Test
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Python found
echo.

REM Check if virtual environment exists
if not exist "AI_Employee_Vault\venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo [INFO] Please run: cd AI_Employee_Vault ^&^& python -m venv venv
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call AI_Employee_Vault\venv\Scripts\activate.bat

echo [INFO] Checking dependencies...
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Playwright not installed
    echo [INFO] Installing Playwright...
    pip install playwright
    playwright install chromium
)

echo.
echo [INFO] Running validation tests...
echo.

python scripts\test_twitter_browser.py

if errorlevel 1 (
    echo.
    echo [ERROR] Validation failed. Please fix issues before proceeding.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Validation Complete
echo ============================================================
echo.
echo Next steps:
echo 1. Add Twitter credentials to .env file
echo 2. Run: test_twitter_post.bat (for live posting test)
echo 3. Create task in Inbox to trigger automated posting
echo.

pause
