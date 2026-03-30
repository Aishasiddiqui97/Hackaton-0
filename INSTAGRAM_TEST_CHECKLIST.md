# Instagram Playwright Automation - Complete Test Checklist

Complete testing guide for the Instagram Playwright automation system on Windows.

## Prerequisites

Before testing, ensure:
- [ ] Python 3.12+ installed
- [ ] Playwright installed: `pip install playwright`
- [ ] Chromium browser installed: `playwright install chromium`
- [ ] MCP SDK installed: `pip install mcp anthropic`
- [ ] PM2 installed: `npm install -g pm2 pm2-windows-startup`
- [ ] .env file created with INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD
- [ ] DRY_RUN=true in .env (for safe testing)

---

## TEST 1: Session Manager Test

**Objective:** Verify session manager can login and save cookies

### Steps:

1. **Run session manager test:**
```bash
cd AI_Employee_Vault/instagram
python session_manager.py --test
```

2. **Expected behavior:**
   - Browser opens (visible, not headless)
   - Navigates to Instagram login page
   - Types username character by character
   - Types password character by character
   - Clicks login button
   - Handles "Save Login Info" popup (clicks "Not Now")
   - Handles "Turn on Notifications" popup (clicks "Not Now")
   - Reaches home feed
   - Saves session to `.state/ig_session.json`
   - Browser stays open for 10 seconds

3. **Verify:**
```bash
ls AI_Employee_Vault/.state/ig_session.json
ls AI_Employee_Vault/.state/ig_session_meta.json
```

### Success Criteria:
- ✅ Browser opens and logs in successfully
- ✅ Session files created in `.state/` directory
- ✅ No errors in console
- ✅ Home feed visible before browser closes

### Troubleshooting:
- **If login fails with captcha:** Instagram detected automation. Try:
  1. Log in manually in browser once
  2. Wait 24 hours before retrying
  3. Check if VPN is enabled (disable it)
- **If wrong password error:** Check INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env
- **If 2FA prompt:** Temporarily disable 2FA or add 2FA handling code

---

## TEST 2: DRY RUN Post Test

**Objective:** Verify post action works in DRY_RUN mode (no actual posting)

### Steps:

1. **Ensure DRY_RUN is enabled:**
```bash
grep DRY_RUN AI_Employee_Vault/../.env
# Should show: DRY_RUN=true
```

2. **Create test image:**
```bash
# Place any image file at:
AI_Employee_Vault/test_image.jpg
```

3. **Run post test:**
```bash
cd AI_Employee_Vault/instagram
python instagram_actions.py --test-post
```

4. **Expected output:**
```
[DRY RUN] Would post photo to Instagram
  Image: AI_Employee_Vault/test_image.jpg
  Caption: Test post from automation...
  Hashtags: test, automation, instagram
```

5. **Verify log:**
```bash
cat AI_Employee_Vault/Logs/instagram_posts.json
```

### Success Criteria:
- ✅ Script runs without errors
- ✅ Shows "DRY RUN" message
- ✅ Does NOT actually post to Instagram
- ✅ Log entry created with `"dry_run": true`

---

## TEST 3: Get Profile Stats Test

**Objective:** Verify can scrape profile statistics

### Steps:

1. **Run stats test:**
```bash
cd AI_Employee_Vault/instagram
python instagram_actions.py --test-stats
```

2. **Expected behavior:**
   - Browser opens
   - Logs in (or reuses session)
   - Navigates to profile page
   - Scrapes followers, following, posts count
   - Displays stats
   - Logs out

3. **Expected output:**
```
Stats: {'followers': 123, 'following': 456, 'posts': 78, 'timestamp': '...'}
```

### Success Criteria:
- ✅ Browser opens and navigates to profile
- ✅ Stats are scraped correctly
- ✅ Numbers match actual Instagram profile
- ✅ No errors

---

## TEST 4: MCP Server Test

**Objective:** Verify MCP server can be started and responds to tool calls

### Steps:

1. **Start MCP server manually:**
```bash
cd AI_Employee_Vault/mcp_servers
python instagram_mcp_server.py
```

2. **Server should start and wait for input** (stdio mode)

3. **Test with simple JSON request** (in another terminal):
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python instagram_mcp_server.py
```

4. **Expected:** List of available tools returned

5. **Stop server:** Ctrl+C

### Success Criteria:
- ✅ Server starts without errors
- ✅ Responds to tool list request
- ✅ Shows 6 Instagram tools

---

## TEST 5: Watcher Single Cycle Test

**Objective:** Verify watcher can check comments/DMs once

### Steps:

1. **Modify watcher for single run:**
```bash
cd AI_Employee_Vault/watchers
```

2. **Run watcher manually (will run once then you can Ctrl+C):**
```bash
python instagram_watcher.py
```

3. **Expected behavior:**
   - Checks comments
   - Checks DMs
   - Creates action files if keywords found
   - Saves processed IDs
   - Waits for next cycle (Ctrl+C to stop)

4. **Verify state file:**
```bash
cat AI_Employee_Vault/.state/instagram_processed.json
```

### Success Criteria:
- ✅ Watcher runs without crashing
- ✅ Checks comments and DMs
- ✅ Creates action files if keywords found
- ✅ State file created/updated

---

## TEST 6: HITL Approval Tool Test

**Objective:** Verify approval tool can list and approve items

### Steps:

1. **Create test approval file:**
```bash
mkdir -p AI_Employee_Vault/Pending_Approval/social

cat > AI_Employee_Vault/Pending_Approval/social/IG_DRAFT_TEST.md << 'EOF'
---
type: instagram_draft
platform: instagram
scheduled_time: 2026-03-30 10:00 AM
image_needed: true
status: pending_approval
---

## Caption
This is a test post for approval system!

## Hashtags
test automation instagram

## Why This Post
Testing the HITL approval workflow
EOF
```

2. **List pending approvals:**
```bash
cd AI_Employee_Vault
python approve.py --list
```

3. **Expected:** Shows the test draft

4. **Preview the draft:**
```bash
python approve.py --preview IG_DRAFT_TEST.md
```

5. **Approve the draft:**
```bash
python approve.py --approve IG_DRAFT_TEST.md
```

6. **Verify moved to Approved:**
```bash
ls Approved/IG_DRAFT_TEST.md
```

### Success Criteria:
- ✅ Tool lists pending items
- ✅ Preview shows full content
- ✅ Approval moves file to Approved/
- ✅ Log entry created in Logs/approvals.json

---

## TEST 7: PM2 Process Manager Test

**Objective:** Verify watcher runs permanently with PM2

### Steps:

1. **Start watcher with PM2:**
```bash
cd AI_Employee_Vault
start_all.bat
```

2. **Check status:**
```bash
pm2 status
```

3. **Expected:** Shows `instagram-watcher` as `online`

4. **View logs:**
```bash
pm2 logs instagram-watcher --lines 20
```

5. **Test auto-restart:**
```bash
pm2 restart instagram-watcher
```

6. **Verify it restarted:**
```bash
pm2 status
```

7. **Save configuration:**
```bash
pm2 save
```

### Success Criteria:
- ✅ Watcher starts with PM2
- ✅ Shows as "online" in status
- ✅ Logs show watcher checking Instagram
- ✅ Auto-restarts when killed
- ✅ Configuration saved

---

## TEST 8: End-to-End Comment Reply Flow

**Objective:** Test complete workflow from comment detection to reply

### Steps:

1. **Post a test comment on your Instagram** (from another account or ask someone):
   - Comment with keyword like "How much does this cost?"

2. **Wait for watcher to detect** (up to 15 minutes):
```bash
pm2 logs instagram-watcher
```

3. **Check for action file:**
```bash
ls AI_Employee_Vault/Needs_Action/INSTAGRAM_comment_*.md
```

4. **Review the action file:**
```bash
cat AI_Employee_Vault/Needs_Action/INSTAGRAM_comment_*.md
```

5. **List pending approvals:**
```bash
cd AI_Employee_Vault
python approve.py --list
```

6. **Approve the reply:**
```bash
python approve.py --approve INSTAGRAM_comment_[filename].md
```

7. **Verify file moved to Approved:**
```bash
ls Approved/INSTAGRAM_comment_*.md
```

8. **Check if reply was posted** (if DRY_RUN=false):
   - Go to Instagram and check the comment thread

### Success Criteria:
- ✅ Watcher detects comment with keyword
- ✅ Creates action file with suggested reply
- ✅ Approval tool allows review
- ✅ File moves to Approved after approval
- ✅ Reply posts successfully (if not DRY_RUN)

---

## TEST 9: Real Post Test (CAREFUL!)

**Objective:** Test actual posting to Instagram (NOT DRY RUN)

### ⚠️ WARNING: This will actually post to Instagram!

### Steps:

1. **Prepare test image:**
   - Use a clearly marked test image
   - Caption should say "TEST POST - IGNORE"

2. **Temporarily disable DRY_RUN:**
```bash
# Edit .env file
DRY_RUN=false
```

3. **Create approval file:**
```bash
cat > AI_Employee_Vault/Approved/IG_POST_TEST.md << 'EOF'
---
type: instagram_post
approved: true
---
Test post approved
EOF
```

4. **Run post action:**
```bash
cd AI_Employee_Vault/instagram
python instagram_actions.py --test-post
```

5. **Expected:**
   - Browser opens
   - Logs in
   - Clicks "New Post"
   - Uploads image
   - Types caption
   - Clicks "Share"
   - Post appears on Instagram

6. **Verify on Instagram:**
   - Check your profile
   - Test post should be visible

7. **IMMEDIATELY re-enable DRY_RUN:**
```bash
# Edit .env file
DRY_RUN=true
```

8. **Delete test post from Instagram**

### Success Criteria:
- ✅ Post uploads successfully
- ✅ Appears on Instagram profile
- ✅ Screenshot saved in Logs/
- ✅ Log entry created

---

## TEST 10: Error Recovery Test

**Objective:** Verify system handles errors gracefully

### Steps:

1. **Test with wrong credentials:**
```bash
# Temporarily change password in .env to wrong value
# Run session manager test
python AI_Employee_Vault/instagram/session_manager.py --test
```

2. **Expected:**
   - Login fails
   - Screenshot saved: `Logs/login_failed_[timestamp].png`
   - Signal created: `Signals/INSTAGRAM_LOGIN_FAILED.md`
   - Script exits (does NOT retry)

3. **Verify signal file:**
```bash
cat AI_Employee_Vault/Signals/INSTAGRAM_LOGIN_FAILED.md
```

4. **Restore correct credentials in .env**

5. **Test watcher error handling:**
```bash
# Stop Instagram watcher
pm2 stop instagram-watcher

# Kill Python process manually
# PM2 should auto-restart it

pm2 status
```

6. **Expected:** PM2 restarts watcher automatically

### Success Criteria:
- ✅ Login failure creates signal file
- ✅ Screenshot captured on error
- ✅ Script does NOT auto-retry
- ✅ PM2 auto-restarts crashed processes
- ✅ Error logged properly

---

## Troubleshooting Guide

### Issue: Browser doesn't open
**Solution:**
- Check Playwright installed: `playwright install chromium`
- Try running as administrator
- Check antivirus isn't blocking

### Issue: Login fails with captcha
**Solution:**
- Log in manually in browser once
- Wait 24 hours before retrying automation
- Disable VPN
- Use residential IP (not datacenter/VPN)

### Issue: Selectors not found
**Solution:**
- Instagram may have changed UI
- Update selectors in `instagram_actions.py`
- Check Instagram language is English
- Clear browser cache

### Issue: Session expires quickly
**Solution:**
- Instagram may be flagging automation
- Increase random delays
- Reduce action frequency
- Use more human-like behavior

### Issue: PM2 not starting
**Solution:**
```bash
npm install -g pm2 pm2-windows-startup
pm2-startup install
pm2 save
```

### Issue: MCP server not responding
**Solution:**
- Check Python path in mcp.json
- Verify MCP SDK installed: `pip list | grep mcp`
- Check logs: `Logs/mcp_calls.json`

---

## Test Log Template

Use this to track your testing:

```
Date: ___________
Tester: ___________

[ ] TEST 1: Session Manager - PASS / FAIL
    Notes: _________________________________

[ ] TEST 2: DRY RUN Post - PASS / FAIL
    Notes: _________________________________

[ ] TEST 3: Get Profile Stats - PASS / FAIL
    Notes: _________________________________

[ ] TEST 4: MCP Server - PASS / FAIL
    Notes: _________________________________

[ ] TEST 5: Watcher Single Cycle - PASS / FAIL
    Notes: _________________________________

[ ] TEST 6: HITL Approval Tool - PASS / FAIL
    Notes: _________________________________

[ ] TEST 7: PM2 Process Manager - PASS / FAIL
    Notes: _________________________________

[ ] TEST 8: End-to-End Comment Reply - PASS / FAIL
    Notes: _________________________________

[ ] TEST 9: Real Post Test - PASS / FAIL
    Notes: _________________________________

[ ] TEST 10: Error Recovery - PASS / FAIL
    Notes: _________________________________

Overall Status: PASS / FAIL
Issues Found: _________________________________
_________________________________
_________________________________
```

---

## Next Steps After All Tests Pass

1. **Update .env with real credentials**
2. **Keep DRY_RUN=true until ready for production**
3. **Start watcher permanently:** `start_all.bat`
4. **Monitor logs:** `pm2 logs instagram-watcher`
5. **Check daily:** `python approve.py --status`
6. **Review weekly:** `python approve.py --list`

---

## Production Checklist

Before going live (DRY_RUN=false):

- [ ] All 10 tests passed
- [ ] Session manager working reliably
- [ ] Watcher running for 24+ hours without crashes
- [ ] Approval workflow tested end-to-end
- [ ] Error handling verified
- [ ] Backup of session files created
- [ ] Company_Handbook.md created with brand voice
- [ ] Business_Goals.md created with current priorities
- [ ] Rate limits configured (max 2 posts/day)
- [ ] Human monitoring plan in place
- [ ] Emergency stop procedure documented

---

**Remember:** Start with DRY_RUN=true and test thoroughly before enabling real posting!
