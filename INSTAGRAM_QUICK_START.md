# Instagram Playwright Automation - Quick Start Guide

Complete Instagram automation using Playwright browser automation on Windows.

## 🚀 What Was Built

A fully autonomous Instagram management system that:
- ✅ Logs into Instagram once, saves session, reuses forever
- ✅ Posts photos with captions and hashtags (with human approval)
- ✅ Monitors comments for business keywords every 15 minutes
- ✅ Generates suggested replies automatically
- ✅ Checks profile stats (followers, following, posts)
- ✅ Creates weekly performance reports
- ✅ Runs permanently with PM2 (auto-restart on crash)
- ✅ All actions exposed as MCP tools for Claude Code

**Architecture:** Playwright (browser) → MCP Server → Claude Code → Obsidian Vault

---

## 📋 Prerequisites

Before starting, you need:
- ✅ Windows 10/11
- ✅ Python 3.12+ (you have this)
- ✅ Node.js (you have this)
- ✅ Instagram Business/Creator account
- ✅ Instagram username and password

---

## ⚡ Quick Start (10 Minutes)

### Step 1: Create .env File (2 minutes)

```bash
cd "E:\Python.py\Hackaton 0"
copy AI_Employee_Vault\.env.template .env
```

Edit `.env` file with your Instagram credentials:
```
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
DRY_RUN=true
```

**Important:** Keep `DRY_RUN=true` until you've tested everything!

### Step 2: Test Session Manager (3 minutes)

```bash
cd AI_Employee_Vault\instagram
python session_manager.py --test
```

**Expected:** Browser opens, logs into Instagram, saves session, closes.

**If it fails:** Check `Signals\INSTAGRAM_LOGIN_FAILED.md` for details.

### Step 3: Test Profile Stats (2 minutes)

```bash
python instagram_actions.py --test-stats
```

**Expected:** Shows your follower count, following, and posts.

### Step 4: Start the Watcher (1 minute)

```bash
cd ..
start_all.bat
```

**Expected:** PM2 starts the watcher, shows "online" status.

### Step 5: Verify It's Running (2 minutes)

```bash
pm2 status
pm2 logs instagram-watcher --lines 20
```

**Expected:** Logs show "Checking comments..." every 15 minutes.

---

## 🎯 Daily Usage

### Check for Pending Approvals

```bash
cd AI_Employee_Vault
python approve.py --list
```

### Approve a Comment Reply

```bash
python approve.py --preview INSTAGRAM_comment_username_timestamp.md
python approve.py --approve INSTAGRAM_comment_username_timestamp.md
```

### Check System Status

```bash
python approve.py --status
pm2 status
```

### View Watcher Logs

```bash
pm2 logs instagram-watcher
```

---

## 🤖 Using with Claude Code

### Available MCP Tools

Once you configure MCP (see below), you can ask Claude Code:

**"Check my Instagram stats"**
- Calls `instagram_get_stats` tool
- Shows followers, following, posts

**"Check Instagram comments"**
- Calls `instagram_check_comments` tool
- Creates action files for comments with business keywords

**"Generate Instagram weekly summary"**
- Calls `instagram_generate_weekly_summary` tool
- Creates report in `Briefings/`

**"Create an Instagram post about [topic]"**
- Claude reads your business context
- Generates post draft
- Creates approval file in `Pending_Approval/`

### Configure Claude Code MCP

1. **Copy the MCP config:**
```bash
# The file is at: mcp_config_instagram.json
# Copy it to: C:\Users\hp\.config\claude-code\mcp.json
```

2. **If you already have mcp.json, merge it:**
```json
{
  "mcpServers": {
    "instagram-playwright": {
      "command": "python",
      "args": ["E:\\Python.py\\Hackaton 0\\AI_Employee_Vault\\mcp_servers\\instagram_mcp_server.py"],
      "env": {
        "INSTAGRAM_USERNAME": "${INSTAGRAM_USERNAME}",
        "INSTAGRAM_PASSWORD": "${INSTAGRAM_PASSWORD}",
        "DRY_RUN": "true",
        "VAULT_PATH": "E:\\Python.py\\Hackaton 0\\AI_Employee_Vault"
      }
    }
  }
}
```

3. **Restart Claude Code**

4. **Test it:**
Ask Claude Code: "Check my Instagram stats"

---

## 📁 Important Files & Directories

### Configuration
- `.env` - Your Instagram credentials (NEVER commit to git)
- `mcp_config_instagram.json` - MCP server configuration

### Core System
- `AI_Employee_Vault/instagram/session_manager.py` - Handles login
- `AI_Employee_Vault/instagram/instagram_actions.py` - All Instagram actions
- `AI_Employee_Vault/mcp_servers/instagram_mcp_server.py` - MCP server
- `AI_Employee_Vault/watchers/instagram_watcher.py` - Continuous monitoring

### Human Interaction
- `AI_Employee_Vault/approve.py` - Approval tool
- `AI_Employee_Vault/Needs_Action/` - Items needing your attention
- `AI_Employee_Vault/Pending_Approval/` - Drafts awaiting approval
- `AI_Employee_Vault/Approved/` - Approved items (Claude executes these)

### Monitoring
- `AI_Employee_Vault/Logs/` - All logs
- `AI_Employee_Vault/Signals/` - Error alerts
- `AI_Employee_Vault/Briefings/` - Weekly reports

### Session & State
- `AI_Employee_Vault/.state/ig_session.json` - Saved login session
- `AI_Employee_Vault/.state/instagram_processed.json` - Processed comments/DMs

---

## 🔒 Safety Features

### DRY_RUN Mode (Default: ON)
- Prevents actual posting to Instagram
- Logs what WOULD happen
- Safe for testing

**To enable real posting:**
```bash
# Edit .env
DRY_RUN=false
```

### Human-in-the-Loop (HITL)
- All posts require approval file in `Approved/`
- All comment replies require approval
- Easy preview before approval

### Rate Limits
- Max 2 posts per day
- Max 5 actions per session
- Prevents Instagram from flagging account

### Error Handling
- Never auto-retries failed logins
- Screenshots on all failures
- Signal files for human attention
- Exponential backoff on errors

---

## 🧪 Testing Checklist

Before going live, complete all tests in:
**`INSTAGRAM_TEST_CHECKLIST.md`**

10 comprehensive tests covering:
1. Session Manager
2. DRY RUN Post
3. Profile Stats
4. MCP Server
5. Watcher Single Cycle
6. HITL Approval Tool
7. PM2 Process Manager
8. End-to-End Comment Reply
9. Real Post (careful!)
10. Error Recovery

**Estimated time:** 1-2 hours

---

## 🚨 Troubleshooting

### Login Fails with Captcha
**Solution:**
- Log in manually in browser once
- Wait 24 hours before retrying automation
- Disable VPN
- Use residential IP (not datacenter)

### Session Expires Quickly
**Solution:**
- Instagram may be flagging automation
- Increase random delays in code
- Reduce action frequency
- More human-like behavior

### Watcher Not Creating Files
**Check:**
1. `pm2 logs instagram-watcher` for errors
2. `.env` has correct INSTAGRAM_USERNAME
3. `DRY_RUN` setting
4. `Signals/INSTAGRAM_WATCHER_ERROR.md`

### MCP Tools Not Working
**Check:**
1. MCP server path in mcp.json is correct
2. Python path is correct
3. `Logs/mcp_calls.json` for errors
4. Restart Claude Code

### Browser Doesn't Open
**Solution:**
- Run: `playwright install chromium`
- Try running as administrator
- Check antivirus isn't blocking

---

## 📊 Monitoring & Maintenance

### Daily
- Check `Needs_Action/` for new comments
- Review `Signals/` for errors
- Verify watcher running: `pm2 status`

### Weekly
- Generate summary: Ask Claude "Generate Instagram weekly summary"
- Review posting frequency (2-3 posts/week ideal)
- Check follower growth
- Analyze top posts

### Monthly
- Review hashtag strategy
- Update `Company_Handbook.md` if brand voice changes
- Check session file age (refresh if > 30 days)

---

## 🎓 Learning Resources

### Documentation
- `INSTAGRAM_TEST_CHECKLIST.md` - Complete testing guide
- `Plans/INSTAGRAM_BUILD_PROGRESS.md` - Build tracker
- `AI_Employee_Vault/.claude/skills/instagram_agent.md` - Claude Code skill

### Logs to Monitor
- `Logs/instagram_posts.json` - All post attempts
- `Logs/mcp_calls.json` - All MCP tool calls
- `Logs/pm2/` - PM2 process logs
- `Signals/` - Error signals

---

## ⚠️ Important Notes

1. **Start with DRY_RUN=true** - Test thoroughly before enabling real posting
2. **Never commit .env** - Contains your Instagram password
3. **Respect rate limits** - Max 2 posts/day to avoid Instagram flags
4. **Monitor Signals/** - Check daily for error alerts
5. **Session reuse** - Login once, cookies saved, reused forever
6. **Human approval required** - All posts/replies need approval first

---

## 🎉 You're Ready!

Your Instagram automation system is complete and ready to use.

**Next Steps:**
1. ✅ Create `.env` with your credentials
2. ✅ Run TEST 1 from `INSTAGRAM_TEST_CHECKLIST.md`
3. ✅ If test passes, continue with remaining tests
4. ✅ Configure Claude Code MCP
5. ✅ Start using: `start_all.bat`

**Questions?**
- Check `INSTAGRAM_TEST_CHECKLIST.md` for detailed testing
- Check `Plans/INSTAGRAM_BUILD_PROGRESS.md` for build details
- Check `Signals/` directory for error messages

---

**Built:** 2026-03-30
**Status:** ✅ Complete - Ready for Testing
**Files:** 12 files, ~3,585 lines of code
**Platform:** Windows with Playwright browser automation
