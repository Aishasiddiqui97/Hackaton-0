@echo off
REM Start Twitter MCP Server with Autonomous Login
echo ========================================
echo Twitter MCP Server - Autonomous Login
echo ========================================
echo.
echo Starting server with auto-login enabled...
echo.
echo What will happen:
echo 1. Server starts on port 3006
echo 2. Checks for existing session
echo 3. If session exists: Instant login (no browser)
echo 4. If no session: Browser opens, logs in, saves session
echo 5. Future runs: Instant (session restored)
echo.
echo First run: Browser will open for login
echo Subsequent runs: Instant login from saved session
echo.
echo Press Ctrl+C to stop server
echo ========================================
echo.

cd /d "%~dp0"
node mcp_servers/twitter_mcp.js
