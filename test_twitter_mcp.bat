@echo off
REM Test Twitter MCP Server
echo Testing Twitter MCP Server...
cd /d "%~dp0"

echo.
echo [1/3] Checking server health...
curl -s http://localhost:3006/health

echo.
echo.
echo [2/3] Testing login...
curl -X POST http://localhost:3006/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"%TWITTER_USERNAME%\",\"password\":\"%TWITTER_PASSWORD%\"}"

echo.
echo.
echo [3/3] Testing tweet post...
curl -X POST http://localhost:3006/post_tweet ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Testing autonomous Twitter integration from Gold Tier Digital FTE! #AI #Automation\"}"

echo.
echo.
echo Test complete! Check AI_Employee_Vault/Logs/Twitter_Log.md for results.
pause
