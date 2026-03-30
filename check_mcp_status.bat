@echo off
REM Check if Twitter MCP Server is running
echo Checking Twitter MCP Server status...
echo.

curl -s http://localhost:3006/health 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ✓ Server is running on port 3006
    echo.
    echo You can now test login with:
    echo   python test_mcp_connection.py
) else (
    echo ✗ Server is NOT running
    echo.
    echo Start the server first:
    echo   .\start_twitter_mcp.bat
    echo.
    echo Keep that terminal open, then run this check again.
)

pause
