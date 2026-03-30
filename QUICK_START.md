# Quick Start Guide - Twitter MCP Connection

## Step-by-Step (3 Terminals)

### Terminal 1: Start MCP Server (KEEP THIS OPEN)
```powershell
cd "E:\Python.py\Hackaton 0"
.\start_twitter_mcp.bat
```
**Expected output:**
```
Starting Twitter MCP Server on port 3006...
🚀 Twitter MCP Server Started
📡 Listening on: http://localhost:3006
```
**⚠️ DO NOT CLOSE THIS TERMINAL - Keep it running!**

---

### Terminal 2: Test Connection
```powershell
cd "E:\Python.py\Hackaton 0"
python test_mcp_connection.py
```

This will:
1. Check server health
2. Attempt login (browser will open)
3. If 2FA appears, enter code manually
4. Session will be saved for future use

---

### Terminal 3: Test Tweet (After Login Success)
```powershell
curl -X POST http://localhost:3006/post_tweet -H "Content-Type: application/json" -d "{\"text\":\"Testing Twitter MCP integration! 🚀\"}"
```

---

## Troubleshooting

**Server won't start?**
```powershell
# Check if port 3006 is already in use
netstat -ano | findstr 3006

# If something is using it, kill the process or change port in twitter_mcp.js
```

**Login fails?**
- Check username in .env (should be @AISHA726035158)
- Verify password is correct
- If 2FA appears, enter code in browser
- Session saves after first successful login

**Browser doesn't open?**
- Check if Playwright is installed: `npx playwright install chromium`
- Check MCP server terminal for errors

---

## Quick Test (Without Login)
```powershell
# Just check if server is responding
curl http://localhost:3006/health
```

Expected response:
```json
{"status":"running","port":3006,"loggedIn":false}
```
