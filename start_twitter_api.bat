@echo off
REM Start Twitter API Server (No Browser!)
echo ========================================
echo Twitter API Server - No Browser Needed
echo ========================================
echo.
echo Starting API-based server on port 3007...
echo.
echo Benefits:
echo   ✓ No browser automation
echo   ✓ No login issues
echo   ✓ Fast and reliable
echo   ✓ No automation detection
echo.
echo Press Ctrl+C to stop server
echo ========================================
echo.

cd /d "%~dp0"
node mcp_servers/twitter_api_server.js
