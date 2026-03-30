@echo off
cls
echo.
echo ========================================
echo   BROWSER SESSION CHECK
echo ========================================
echo.
echo You mentioned browser is open and logged in.
echo Let's use that session for automation!
echo.
echo ========================================
echo.

REM Check if browser MCP server is running
echo [Check 1/3] Checking if browser server is running...
curl -s http://localhost:3006/health >nul 2>&1

if %errorlevel% equ 0 (
    echo   √ Browser server is running on port 3006
    echo.

    REM Check login status
    echo [Check 2/3] Checking login status...
    curl -s http://localhost:3006/health > temp_health.json 2>nul

    findstr /C:"loggedIn" temp_health.json >nul
    if %errorlevel% equ 0 (
        echo   √ Server reports login status
        type temp_health.json
        echo.
    )
    del temp_health.json 2>nul

) else (
    echo   X Browser server not running
    echo.
    echo   Start it: .\start_twitter_autonomous.bat
    echo.
)

echo [Check 3/3] Recommendation...
echo.
echo ========================================
echo   RECOMMENDED ACTION
echo ========================================
echo.
echo Since you have browser open and logged in:
echo.
echo 1. START BROWSER SERVER:
echo    .\start_twitter_autonomous.bat
echo.
echo 2. SERVER WILL:
echo    - Detect your existing login
echo    - Use your browser session
echo    - Post tweets automatically
echo.
echo 3. TEST IT:
echo    python test_autonomous_login.py
echo.
echo ========================================
echo.
echo Press any key to start browser server...
pause >nul

echo.
echo Starting browser MCP server...
echo.
start cmd /k "cd /d "%~dp0" && .\start_twitter_autonomous.bat"

echo.
echo ========================================
echo   BROWSER SERVER STARTED
echo ========================================
echo.
echo Watch the new terminal window.
echo.
echo You should see:
echo   - Browser opens (or uses existing)
echo   - Checks session
echo   - "Logged in (session restored)" OR
echo   - "Login successful"
echo   - "Server ready"
echo.
echo Press any key to test it...
pause >nul

echo.
echo Testing browser automation...
echo.
python test_autonomous_login.py

echo.
echo ========================================
echo   RESULT
echo ========================================
echo.
echo If you saw:
echo   √ Auto-login successful
echo   √ Tweet posted successfully
echo.
echo Then browser automation is WORKING!
echo.
echo Your Twitter integration is ready!
echo   - No API credentials needed
echo   - Uses browser session
echo   - Posts tweets automatically
echo.
pause
