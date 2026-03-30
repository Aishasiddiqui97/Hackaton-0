# Twitter/X Browser Automation - Complete Setup Guide

## Overview

This guide covers the Twitter/X browser automation agent that uses Playwright to autonomously post tweets with human oversight and retry logic.

---

## 🎯 What It Does

The Twitter Browser Agent can:
- **Autonomously login** to X (Twitter) account
- **Generate AI-focused tweets** about automation and digital employees
- **Post tweets** with hashtags
- **Capture tweet URLs** for tracking
- **Log all activities** to vault
- **Retry on failures** using Ralph Wiggum loop
- **Require human approval** for all posts (Medium risk)

---

## 📋 Prerequisites

### 1. Twitter/X Account
- Active Twitter/X account
- Email and password credentials
- 2FA disabled (or use app-specific password)

### 2. Python Dependencies
```bash
pip install playwright python-dotenv
playwright install chromium
```

### 3. Vault Structure
```
AI_Employee_Vault/
├── Agents/
│   └── X_Twitter_MCP_Agent.md
├── Plans/
│   └── Twitter_Post_Plan.md
└── Logs/
    └── Twitter_Log.md
```

---

## 🔧 Installation

### Step 1: Install Playwright

```bash
# Install Python package
pip install playwright

# Install browser binaries
playwright install chromium
```

### Step 2: Configure Credentials

Add to `.env` file:
```bash
# Twitter/X Browser Credentials
TWITTER_EMAIL=your_twitter_email@gmail.com
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
```

### Step 3: Test Installation

```bash
# Run test suite
python scripts/test_twitter_browser.py
```

Expected output:
```
✅ PASS - Playwright Installation
✅ PASS - Vault Structure
✅ PASS - Log File
✅ PASS - Tweet Generation
✅ PASS - Browser Initialization

Total: 5/5 tests passed
```

---

## 🚀 Usage

### Method 1: Direct Script Execution

```bash
# Test with real posting (requires confirmation)
python scripts/test_twitter_post.py
```

This will:
1. Load credentials from .env
2. Ask for confirmation
3. Start browser automation
4. Login to Twitter
5. Generate and post tweet
6. Capture URL
7. Save log
8. Logout

### Method 2: Via Task in Inbox

Create file: `AI_Employee_Vault/Inbox/post_twitter.md`

```markdown
# Post Twitter Update

Post tweet about our AI automation achievements.

Risk Level: Medium
```

The system will:
1. Detect task in Inbox
2. Move to Needs_Action for approval
3. After approval, execute browser automation
4. Post tweet
5. Log results
6. Move to Done

### Method 3: Via MCP Server

Send JSON request to MCP server:
```json
{
  "action": "autonomous_post",
  "email": "your_email@example.com",
  "password": "your_password"
}
```

---

## 📊 Workflow Details

### Complete Execution Flow

```
1. Initialize
   ├─ Load credentials from .env
   ├─ Start Playwright browser
   └─ Navigate to x.com/login

2. Authenticate
   ├─ Enter email/username
   ├─ Click Next
   ├─ Enter password
   ├─ Click Login
   └─ Wait for home timeline

3. Generate Content
   ├─ Select random AI-focused tweet
   ├─ Ensure ≤ 280 characters
   └─ Add hashtags

4. Post Tweet
   ├─ Click "Post" button
   ├─ Enter tweet content
   ├─ Click "Post" to publish
   └─ Wait for confirmation

5. Capture Results
   ├─ Navigate to profile
   ├─ Find latest tweet
   └─ Copy tweet URL

6. Log Activity
   ├─ Create log entry
   ├─ Save to Twitter_Log.md
   └─ Include timestamp, content, URL

7. Cleanup
   ├─ Logout from account
   ├─ Close browser
   └─ Clear session
```

---

## 🛡️ Error Handling

### Login Failures
- **Retry:** Up to 3 attempts
- **Wait:** 10 seconds between attempts
- **Log:** All failure reasons
- **Escalate:** After 3 failures

### Post Failures
- **Retry:** Once
- **Check:** Rate limits
- **Verify:** Content length
- **Log:** Error details

### Network Errors
- **Wait:** 10 seconds
- **Retry:** Operation
- **Continue:** With partial success

---

## 📝 Sample Tweet Content

The agent generates tweets like:

```
AI employees are not replacing humans — they're giving businesses
superpowers. A Digital FTE can work 24/7, handle operations, and
scale instantly. The future of work is human + AI collaboration.
#AI #Automation #DigitalEmployee
```

```
Building autonomous AI agents that actually work is harder than it
looks. But when done right, they transform how businesses operate.
Here's what I learned building a Digital FTE system.
#AIAutomation #FutureOfWork
```

---

## 🔍 Monitoring & Logs

### Log Files

**Browser Actions:** `logs/twitter_browser_actions.log`
```
[2026-02-19 10:30:15] [TWITTER_BROWSER] INFO - TWITTER_BROWSER_START
[2026-02-19 10:30:18] [TWITTER_BROWSER] INFO - TWITTER_LOGIN_SUCCESS
[2026-02-19 10:30:45] [TWITTER_BROWSER] INFO - TWITTER_POST_SUCCESS
[2026-02-19 10:30:50] [TWITTER_BROWSER] INFO - TWITTER_LOG_SUCCESS
```

**Activity Log:** `AI_Employee_Vault/Logs/Twitter_Log.md`
```markdown
---

## Tweet Log Entry

**Date:** 2026-02-19 10:30:45

**Tweet Content:**
AI employees are not replacing humans — they're giving businesses superpowers...

**Tweet URL:** https://x.com/username/status/123456789

**Status:** Posted

**Agent:** X_Twitter_MCP_Agent

---
```

---

## ⚙️ Configuration Options

### Browser Settings

Edit `mcp_servers/twitter_browser_server.py`:

```python
# Headless mode (no visible browser)
headless=True  # Change to False for debugging

# Browser viewport
viewport={'width': 1920, 'height': 1080}

# Timeout settings
timeout=30000  # 30 seconds
```

### Retry Settings

```python
# Login retries
max_retries=3

# Post retries
max_retries=3

# Wait between retries
time.sleep(10)
```

---

## 🔒 Security Best Practices

1. **Never commit credentials**
   - Use .env file (gitignored)
   - Rotate passwords regularly

2. **Use app-specific passwords**
   - If 2FA enabled, generate app password
   - Store securely

3. **Monitor activity**
   - Review logs regularly
   - Check Twitter_Log.md for all posts

4. **Human approval required**
   - All posts go through Needs_Action
   - Review before approval

---

## 🐛 Troubleshooting

### Issue: Browser won't start
**Solution:**
```bash
playwright install chromium
```

### Issue: Login fails
**Causes:**
- Wrong credentials
- 2FA enabled
- Rate limited

**Solution:**
- Verify credentials in .env
- Disable 2FA or use app password
- Wait 15 minutes if rate limited

### Issue: Tweet not posting
**Causes:**
- Content too long (>280 chars)
- Rate limit reached
- Network timeout

**Solution:**
- Check tweet length
- Wait for rate limit reset
- Increase timeout setting

### Issue: Can't find tweet URL
**Cause:**
- Tweet not appearing on timeline

**Solution:**
- Increase wait time after posting
- Check Twitter web interface manually

---

## 📈 Performance Metrics

- **Average execution time:** 2-3 minutes
- **Success rate target:** >95%
- **Max retry attempts:** 3
- **Timeout per action:** 30 seconds

---

## 🔄 Integration with Digital FTE

### Workflow Integration

```
Gmail Watcher → Detects "Post to Twitter" request
     ↓
Reasoning Engine → Creates plan
     ↓
Risk Assessment → Medium risk (requires approval)
     ↓
Needs_Action → Human reviews and approves
     ↓
Twitter Browser Agent → Executes posting
     ↓
Twitter_Log.md → Records activity
     ↓
Done → Task completed
```

### MCP Server Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "twitter-browser-server": {
      "command": "python",
      "args": ["E:\\Python.py\\Hackaton 0\\mcp_servers\\twitter_browser_server.py"]
    }
  }
}
```

---

## 🎯 Success Criteria

System is working when:
- ✅ All 5 validation tests pass
- ✅ Browser opens and navigates to Twitter
- ✅ Login succeeds
- ✅ Tweet posts successfully
- ✅ URL captured and logged
- ✅ Clean logout

---

## 🚀 Next Steps

1. **Run validation:** `python scripts/test_twitter_browser.py`
2. **Test posting:** `python scripts/test_twitter_post.py`
3. **Create task:** Add task to Inbox for automated posting
4. **Monitor logs:** Check Twitter_Log.md for activity
5. **Schedule posts:** Set up content calendar

---

## 📚 Related Documentation

- `AI_Employee_Vault/Agents/X_Twitter_MCP_Agent.md` - Agent overview
- `AI_Employee_Vault/Skills/twitter_browser_poster.md` - Skill details
- `AI_Employee_Vault/Plans/Twitter_Post_Plan.md` - Execution plan
- `logs/twitter_browser_actions.log` - Technical logs

---

**Status:** ✅ Complete and Ready for Use

**Last Updated:** 2026-02-19
