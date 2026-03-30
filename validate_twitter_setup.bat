@echo off
REM Complete validation of Twitter integration
echo ========================================
echo Twitter Integration - Complete Validation
echo ========================================
echo.

cd /d "%~dp0"

echo [Step 1/5] Checking dependencies...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo   X Node.js not found
    goto :error
)
echo   √ Node.js installed

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   X Python not found
    goto :error
)
echo   √ Python installed

echo.
echo [Step 2/5] Checking configuration...
if not exist ".env" (
    echo   X .env file not found
    echo   Run: copy .env.template .env
    goto :error
)
echo   √ .env file exists

if not exist "sessions\twitter" (
    echo   ! sessions\twitter directory missing (will be created)
    mkdir "sessions\twitter"
)
echo   √ Session directory ready

echo.
echo [Step 3/5] Checking Node.js packages...
if not exist "node_modules" (
    echo   X node_modules not found
    echo   Run: npm install
    goto :error
)
echo   √ Node.js packages installed

echo.
echo [Step 4/5] Checking files...
if not exist "mcp_servers\twitter_mcp.js" (
    echo   X twitter_mcp.js not found
    goto :error
)
echo   √ MCP server file exists

if not exist "scripts\twitter_watcher.py" (
    echo   X twitter_watcher.py not found
    goto :error
)
echo   √ Watcher file exists

if not exist "AI_Employee_Vault\Skills\Twitter_Skill.md" (
    echo   X Twitter_Skill.md not found
    goto :error
)
echo   √ Skill file exists

echo.
echo [Step 5/5] Checking server status...
curl -s http://localhost:3006/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   √ Server is running
    echo.
    echo ========================================
    echo √ ALL CHECKS PASSED
    echo ========================================
    echo.
    echo Your Twitter integration is ready!
    echo.
    echo Server is already running.
    echo Test it: python test_autonomous_login.py
) else (
    echo   ! Server not running
    echo.
    echo ========================================
    echo √ SETUP COMPLETE
    echo ========================================
    echo.
    echo Your Twitter integration is configured!
    echo.
    echo Next step: Start the server
    echo   .\start_twitter_autonomous.bat
    echo.
    echo Then test it:
    echo   python test_autonomous_login.py
)

echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo X VALIDATION FAILED
echo ========================================
echo.
echo Please fix the errors above and try again.
echo.
echo Quick fix:
echo   .\setup_twitter_integration.bat
echo.
pause
exit /b 1
