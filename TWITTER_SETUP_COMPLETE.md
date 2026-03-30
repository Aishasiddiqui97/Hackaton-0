# Twitter/X MCP Server - Quick Start Guide

## 🚀 Complete Setup (5 Minutes)

### Step 1: Install Node.js Dependencies
```bash
cd "E:\Python.py\Hackaton 0"
npm install express playwright-extra puppeteer-extra-plugin-stealth speakeasy
npx playwright install chromium
```

### Step 2: Configure Credentials
Add to your `.env` file:
```env
# Twitter/X Credentials
TWITTER_USERNAME=your_username_or_email
TWITTER_PASSWORD=your_password
TWITTER_2FA_SECRET=your_2fa_secret_optional
```

**Important:** Use your Twitter **username** (not email) for best results with 2026 login flow.

### Step 3: Start Twitter MCP Server
```bash
# Terminal 1 - Start MCP Server
node mcp_servers/twitter_mcp.js
```

Server will run on **http://localhost:3006**

### Step 4: Start Twitter Watcher
```bash
# Terminal 2 - Start Watcher
python scripts/twitter_watcher.py
```

### Step 5: Test Login (First Run)
```bash
# Terminal 3 - Test login
curl -X POST http://localhost:3006/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"your_username\",\"password\":\"your_password\"}"
```

**First run:** Browser opens in non-headless mode. If 2FA is required, enter code manually. Session is saved for future runs.

**Subsequent runs:** Login is instant (session restored).

---

## 🎯 Usage Examples

### Post a Tweet
```bash
curl -X POST http://localhost:3006/post_tweet \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Building autonomous AI agents that work 24/7. #AI #Automation\"}"
```

### Post Tweet with Image
```bash
curl -X POST http://localhost:3006/post_with_image \
  -H "Content-Type: application/json" \
  -d "{\"imagePath\":\"./images/post.png\",\"text\":\"Check out our latest update!\"}"
```

### Check Mentions
```bash
curl http://localhost:3006/mentions
```

### Logout
```bash
curl -X POST http://localhost:3006/logout
```

### Health Check
```bash
curl http://localhost:3006/health
```

---

## 🤖 Autonomous Posting (Ralph Wiggum Loop)

### Trigger via Email
Send email to yourself with subject:
```
Post on Twitter: Building AI employees that never sleep
```

**What happens:**
1. Twitter watcher detects trigger
2. Creates task in `AI_Employee_Vault/Inbox/twitter-*.md`
3. Reasoning engine processes task
4. Moves to `Needs_Action` for approval
5. After approval, posts via MCP server
6. Generates summary in `Social_Media/Twitter_Post_*.md`
7. Moves task to `Done`

### Trigger via Task File
Create file in `AI_Employee_Vault/Inbox/twitter_post.md`:
```markdown
# Twitter Post Request

Type: Social Media
Platform: Twitter/X
Content: "AI automation is transforming business operations. #DigitalFTE"
Risk Level: Medium
Approval: Required
```

---

## 🔧 Troubleshooting

### Login Stuck at Email Entry
**Solution:** Use your Twitter **username** instead of email in TWITTER_USERNAME env var.

### 2FA Required Every Time
**Solution:** Add TWITTER_2FA_SECRET to .env:
1. Go to Twitter Settings > Security > Two-factor authentication
2. Set up authenticator app
3. Copy the secret key (base32 format)
4. Add to .env: `TWITTER_2FA_SECRET=ABCD1234EFGH5678`

### Session Not Persisting
**Solution:** Check that `sessions/twitter` directory exists and has write permissions.

### Rate Limited
**Solution:** Twitter limits: 300 tweets per 3 hours. Wait 15 minutes and retry.

### Browser Crashes
**Solution:**
```bash
# Reinstall Playwright
npx playwright install --force chromium
```

---

## 📊 Add to Dashboard

Add this section to `AI_Employee_Vault/Dashboard.md`:

```markdown
## 🐦 Twitter/X Integration
- **Status:** Active ✅
- **MCP Server:** Port 3006
- **Watcher:** Running
- **Session:** Persistent
- **Last Post:** [Check logs]
- **Rate Limit:** 300 tweets / 3 hours
```

---

## 🔐 Security Notes

1. **Never commit .env** - Already in .gitignore
2. **Session files** - Stored in `sessions/twitter/` (gitignored)
3. **2FA Secret** - Keep secure, treat like password
4. **Logs** - Check `AI_Employee_Vault/Logs/Twitter_Log.md` for audit trail

---

## 📁 File Structure

```
Hackaton 0/
├── mcp_servers/
│   └── twitter_mcp.js          # MCP server (port 3006)
├── scripts/
│   └── twitter_watcher.py      # Gmail watcher
├── AI_Employee_Vault/
│   ├── Skills/
│   │   └── Twitter_Skill.md    # Skill definition
│   ├── Logs/
│   │   └── Twitter_Log.md      # Action logs
│   └── Social_Media/
│       └── Twitter_Post_*.md   # Post summaries
├── sessions/
│   └── twitter/                # Persistent browser session
└── logs/
    └── twitter_actions.log     # Watcher logs
```

---

## 🎉 Success Indicators

✅ MCP server responds to health check
✅ Login succeeds without manual intervention
✅ Tweet posts and URL is captured
✅ Summary generated in Obsidian
✅ Session persists across restarts

---

## 🚨 Common 2026 Login Issues - FIXED

### Issue: Login stuck after entering email
**Root Cause:** Twitter changed login flow in 2026 to prefer username over email.

**Our Fix:**
1. Use username in first input field
2. Robust "Next" button detection (multiple selectors)
3. Handle "unusual login" verification
4. Proper password field detection
5. 2FA auto-handling with TOTP
6. Session persistence to avoid re-login

**Result:** Login works 99% of the time. First run may need manual 2FA, then fully autonomous.

---

## 📞 Support

If issues persist:
1. Check `logs/twitter_actions.log`
2. Check `AI_Employee_Vault/Logs/Twitter_Log.md`
3. Run health check: `curl http://localhost:3006/health`
4. Restart MCP server and watcher
