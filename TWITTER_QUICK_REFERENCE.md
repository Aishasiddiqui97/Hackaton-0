# 🚀 Twitter/X Integration - Quick Reference

## 📋 Terminal Commands

### Start Services
```bash
# Terminal 1 - MCP Server
start_twitter_mcp.bat
# OR: node mcp_servers/twitter_mcp.js

# Terminal 2 - Watcher
start_twitter_watcher.bat
# OR: python scripts/twitter_watcher.py
```

### Test Integration
```bash
# Full test suite
python test_twitter_integration.py

# Quick test
test_twitter_mcp.bat
```

### Manual API Calls
```bash
# Health check
curl http://localhost:3006/health

# Login
curl -X POST http://localhost:3006/login -H "Content-Type: application/json" -d "{\"username\":\"your_username\",\"password\":\"your_password\"}"

# Post tweet
curl -X POST http://localhost:3006/post_tweet -H "Content-Type: application/json" -d "{\"text\":\"Your tweet here\"}"

# Check mentions
curl http://localhost:3006/mentions

# Logout
curl -X POST http://localhost:3006/logout
```

---

## 🤖 Autonomous Triggers

### Via Email
Send email with subject containing:
- "Post on Twitter"
- "Tweet this"
- "Share on X"
- "Check X mentions"
- "Twitter summary"

### Via Task File
Create `AI_Employee_Vault/Inbox/twitter_post.md`:
```markdown
# Twitter Post Request

Type: Social Media
Platform: Twitter/X
Content: "Your tweet content here #hashtag"
Risk Level: Medium
Approval: Required
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `mcp_servers/twitter_mcp.js` | MCP server (port 3006) |
| `scripts/twitter_watcher.py` | Gmail watcher for triggers |
| `AI_Employee_Vault/Skills/Twitter_Skill.md` | Skill definition |
| `AI_Employee_Vault/Logs/Twitter_Log.md` | Action audit log |
| `AI_Employee_Vault/Social_Media/Twitter_Post_*.md` | Post summaries |
| `sessions/twitter/` | Persistent browser session |
| `logs/twitter_actions.log` | Watcher logs |

---

## 🔧 Environment Variables

Add to `.env`:
```env
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_2FA_SECRET=optional_base32_secret
```

---

## ✅ Success Checklist

- [ ] Node.js dependencies installed
- [ ] Playwright chromium installed
- [ ] .env configured with credentials
- [ ] MCP server starts on port 3006
- [ ] Watcher starts without errors
- [ ] Login succeeds (first run may need manual 2FA)
- [ ] Session persists across restarts
- [ ] Tweet posts successfully
- [ ] Summary generated in Obsidian
- [ ] Dashboard updated

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Login stuck | Use username (not email) in TWITTER_USERNAME |
| 2FA every time | Add TWITTER_2FA_SECRET to .env |
| Session not saved | Check sessions/twitter/ permissions |
| Rate limited | Wait 15 min (300 tweets/3hr limit) |
| Server won't start | `npm install` then `npx playwright install chromium` |

---

## 📊 Integration Status

**Gold Tier Complete** ✅

Same architecture as LinkedIn + Odoo:
- ✅ Watcher monitors Gmail for triggers
- ✅ MCP server handles browser automation
- ✅ Persistent sessions (no re-login)
- ✅ Ralph Wiggum approval loop
- ✅ Obsidian summaries auto-generated
- ✅ Full audit logging
- ✅ 2026 login issues FIXED

**Next Steps:**
1. Run `start_twitter_mcp.bat`
2. Run `start_twitter_watcher.bat`
3. Test with `python test_twitter_integration.py`
4. Send test email: "Post on Twitter: Test message"
5. Check Dashboard for status
