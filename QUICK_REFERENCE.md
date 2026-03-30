# WhatsApp Agent - Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# 1. Test if input box renders
python test_input_box.py

# 2. First time setup (scan QR)
python whatsapp_agent.py --headful

# 3. Run autonomous agent
python autonomous_whatsapp_agent.py
```

---

## 📋 All Launch Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `python test_input_box.py` | Test input box rendering | First run / debugging |
| `python whatsapp_agent.py --headful` | Single scan with browser visible | QR scan / testing |
| `python whatsapp_agent.py --loop` | Loop mode (120s interval) | Scheduled scanning |
| `python autonomous_whatsapp_agent.py` | Continuous autonomous mode | Production / hackathon demo |
| `python whatsapp_agent_force_gpu.py` | Force GPU rendering | If input box fails |
| `python launch_whatsapp_agent.py` | Interactive menu | Easy selection |

---

## 🎯 Interactive Launchers

**Windows:**
```cmd
start_whatsapp.bat
```

**Linux/Mac/Git Bash:**
```bash
bash start_whatsapp.sh
```

---

## 🐳 Docker Commands

**Build:**
```bash
docker build -f Dockerfile.whatsapp -t whatsapp-agent .
```

**Run (Simple):**
```bash
docker run -it --rm \
  --security-opt seccomp=unconfined \
  --cap-add=SYS_ADMIN \
  --shm-size=2g \
  -v $(pwd)/whatsapp_session:/app/whatsapp_session \
  whatsapp-agent
```

**Docker Compose:**
```bash
docker-compose -f docker-compose.whatsapp.yml up -d
docker-compose -f docker-compose.whatsapp.yml logs -f
docker-compose -f docker-compose.whatsapp.yml down
```

---

## 🔧 Troubleshooting Commands

**Clear session (requires QR rescan):**
```bash
# Windows
rmdir /s /q whatsapp_session

# Linux/Mac
rm -rf whatsapp_session/
```

**View logs:**
```bash
# Windows
type logs\whatsapp_agent.log

# Linux/Mac
tail -f logs/whatsapp_agent.log
```

**Check if running:**
```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep whatsapp
```

**Kill process:**
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -f whatsapp_agent
```

---

## 🎨 Browser Args Explained

| Flag | Purpose | Impact |
|------|---------|--------|
| `--no-sandbox` | Disable Chrome sandbox | Required for root/container |
| `--disable-setuid-sandbox` | Extra sandbox bypass | Helps in restricted environments |
| `--disable-dev-shm-usage` | Use /tmp instead of /dev/shm | Prevents memory issues |
| `--disable-software-rasterizer` | Force hardware rendering | **Fixes input box rendering** |
| `--enable-features=NetworkService` | Modern network stack | Stability improvement |
| `--disable-web-security` | Allow cross-origin | Helps with shadow DOM |
| `--use-gl=desktop` | Force desktop GL | Alternative GPU fix |

---

## 📊 Configuration Variables

**In `whatsapp_agent.py`:**
```python
MAX_MESSAGES = 10          # Messages to read per chat
SEND_DELAY_MS = 600        # Typing speed (ms per char)
SCAN_DELAY_S = 5           # Wait after WA loads
CHAT_OPEN_MS = 3000        # Wait after clicking chat
AFTER_SEND_MS = 2000       # Wait after sending
```

**In `autonomous_whatsapp_agent.py`:**
```python
CHECK_INTERVAL = 15        # Seconds between scans
CHAT_LOAD_WAIT = 6         # Wait for virtual scroll
MSG_LOAD_WAIT = 3          # Wait for messages
```

---

## 🔍 Selectors Reference (2025-2026)

**Chat List:**
```python
'#pane-side'                                    # Primary container
'div[aria-label][role="listitem"]'              # Chat rows (2025)
'div[data-testid="cell-frame-container"]'       # Legacy fallback
```

**Messages:**
```python
'div[data-testid="msg-container"]'              # Message container
'span.selectable-text'                          # Message text
'div.message-in'                                # Incoming only
```

**Input Box:**
```python
'div[contenteditable="true"][role="textbox"]'   # Primary (most reliable)
'div[data-testid="conversation-compose-box-input"]'  # Alternative
'footer div[contenteditable="true"]'            # Fallback
```

**Send Button:**
```python
'button[data-testid="send"]'                    # Primary
'button[data-testid="compose-btn-send"]'        # Fallback
```

---

## 🎯 Hackathon Demo Tips

**Slow down for visibility:**
```python
SEND_DELAY_MS = 100        # Slower typing
CHAT_OPEN_MS = 2000        # Visible transitions
CHECK_INTERVAL = 30        # Less frequent scans
```

**Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Show browser window:**
```bash
python autonomous_whatsapp_agent.py  # Already headful=False
# Edit line 41: headless=False (already set)
```

---

## 📁 File Structure

```
.
├── whatsapp_agent.py                    # Main agent (loop mode)
├── autonomous_whatsapp_agent.py         # Continuous autonomous
├── whatsapp_agent_force_gpu.py          # Alternative GPU fix
├── test_input_box.py                    # Input box test
├── launch_whatsapp_agent.py             # Interactive launcher
├── start_whatsapp.bat                   # Windows menu
├── start_whatsapp.sh                    # Linux/Mac menu
├── whatsapp_classifier.py               # Contact classification
├── whatsapp_reply_engine.py             # AI reply generation
├── whatsapp_logger.py                   # Obsidian logging
├── Dockerfile.whatsapp                  # Docker image
├── docker-compose.whatsapp.yml          # Docker orchestration
├── WHATSAPP_INPUT_BOX_FIX.md           # Technical docs
├── PRODUCTION_GUIDE.md                  # Deployment guide
└── whatsapp_session/                    # Browser session (auto-created)
```

---

## ⚡ Performance Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| Memory | 300-500MB | Per browser instance |
| CPU (idle) | 5-15% | Waiting for messages |
| CPU (active) | 30-50% | Processing messages |
| Network | 2-5MB/hour | WhatsApp Web polling |
| Startup time | 10-15s | First load |
| QR scan time | 5-30s | Depends on phone |
| Message processing | 3-5s | Per chat |

---

## 🎓 Learning Resources

**Playwright Docs:**
- https://playwright.dev/python/docs/intro

**WhatsApp Web Reverse Engineering:**
- Inspect with Chrome DevTools (F12)
- Network tab for API calls
- Elements tab for selectors

**Debugging Tips:**
```python
# Take screenshot
page.screenshot(path="debug.png")

# Print HTML
print(page.content())

# Evaluate JavaScript
result = page.evaluate("() => document.title")
```

---

## 🏆 Success Criteria

- [ ] Input box visible and functional
- [ ] Can read incoming messages
- [ ] Can send replies
- [ ] Auto-classification works
- [ ] Obsidian logging works
- [ ] Runs for 1+ hour without crashes
- [ ] Handles network interruptions
- [ ] QR session persists across restarts

---

**Quick Help:** Run `python launch_whatsapp_agent.py` for interactive menu

**Emergency Stop:** Press `Ctrl+C` in terminal

**Reset Everything:** Delete `whatsapp_session/` folder and restart
