@echo off
REM Start Twitter MCP Server
echo Starting Twitter MCP Server on port 3006...
cd /d "%~dp0"
node mcp_servers/twitter_mcp.js
