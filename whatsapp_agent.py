"""
WhatsApp Business Agent – Main Orchestrator
=========================================
Digital FTE that autonomously monitors WhatsApp Web, classifies contacts,
auto-replies with business tone, and logs every conversation to the Obsidian vault.

Usage:
    python whatsapp_agent.py [--loop] [--interval 120]

Options:
    --loop        Keep running and re-scan after each cycle (default: single pass)
    --interval N  Seconds to wait between loop iterations (default: 120)
    --headful     Show the browser window (useful for first-time QR scan)
    --help        Show this help message and exit

First run:
    python whatsapp_agent.py --headful
    (Scan the QR code in the browser window.  Session is saved for future runs.)

Subsequent runs:
    python whatsapp_agent.py --loop
    (Browser runs headless; no QR needed.)
"""

import sys
import time
import argparse
import traceback
from datetime import datetime
from pathlib import Path

# ── Third-party (Playwright) ──────────────────────────────────────────────────
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("[ERROR] Playwright is not installed.")
    print("  Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# ── Local modules ─────────────────────────────────────────────────────────────
from whatsapp_classifier  import classify, is_hot_lead, is_sensitive
from whatsapp_reply_engine import generate_reply, request_human_approval
from whatsapp_logger       import log_conversation

# ─────────────────────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────────────────────

VAULT_ROOT       = Path(__file__).parent
SESSION_DIR      = VAULT_ROOT / "whatsapp_session"
PLAN_FILE        = VAULT_ROOT / "Plan.md"
LOG_FILE         = VAULT_ROOT / "logs" / "whatsapp_agent.log"

WA_URL           = "https://web.whatsapp.com"
MAX_MESSAGES     = 10          # How many recent messages to read per chat
SEND_DELAY_MS    = 600         # ms pause between keystrokes (anti-detection)
SCAN_DELAY_S     = 5           # seconds to wait after opening WA before scanning
CHAT_OPEN_MS     = 3000        # ms to wait after clicking a chat
AFTER_SEND_MS    = 2000        # ms to wait after sending a reply

# Advanced selectors for reliability (Updated for 2025)
SELECTORS = {
    'chat_list': '#pane-side',
    'chat_list_alt': 'div[data-testid="chat-list"]',
    'unread_badge': '[data-testid="icon-unread-count"]',
    'unread_badge_alt': 'span[aria-label*="unread"]',
    'chat_container': 'div[aria-label][role="listitem"]',  # FIX 1: Primary 2025 selector
    'chat_container_alt': 'div[data-testid="cell-frame-container"]',
    'chat_name': 'span[data-testid="cell-frame-title"]',
    'message_container': 'div[data-testid="msg-container"]',
    'message_list_container': '#main div[role="application"]', # FIX: Primary message list container
    'message_list_alt': 'div[data-testid="conversation-panel-messages"]', # FIX: Fallback 1
    'message_list_alt2': 'div.copyable-area', # FIX: Fallback 2
    'message_bubble': 'span.selectable-text',
    'input_box': 'div[data-testid="conversation-compose-box-input"]',  # FIX 3: New primary selector
    'send_button': 'button[data-testid="send"]',  # FIX 3: Updated send button selector
    'back_button': 'button[data-testid="back"]',
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
DEFAULT_TIMEOUT = 30000  # 30 seconds

# ─────────────────────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────────────────────

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def _log(msg: str, level: str = "INFO"):
    ts      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line    = f"{ts} | {level:<8} | {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ─────────────────────────────────────────────────────────────────────────────
#  Plan.md
# ─────────────────────────────────────────────────────────────────────────────

def write_plan(session_start: str, actions: list[str]):
    """Update Plan.md with this session's actions."""
    plan = f"""# WhatsApp Business Agent – Session Plan

**Started:** {session_start}
**Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Process
1. Open web.whatsapp.com (persistent Playwright session)
2. Scan unread chats
3. Classify contact → Lead / Existing Client / Vendor / Unknown
4. Generate business-tone auto-reply
5. Human approval gate for sensitive/payment content
6. Send reply
7. Log conversation to Obsidian `/Inbox` and `/Needs_Action` (hot leads)
8. Repeat until no unread chats remain

## This Session Log

| # | Contact | Category | Hot | Sensitive | Reply Sent |
|---|---------|----------|-----|-----------|------------|
"""
    for a in actions:
        plan += a + "\n"

    plan += "\n---\n_Generated by WhatsApp Business Agent – Digital FTE_\n"
    PLAN_FILE.write_text(plan, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
#  WhatsApp Web Helpers (Playwright)
# ─────────────────────────────────────────────────────────────────────────────


def wait_for_wa_ready(page, headful: bool):
    """Wait for WhatsApp Web to load with multiple robust selector strategies."""
    _log("Waiting for WhatsApp Web to load…")
    try:
        if headful:
            _log("👉 Please scan the QR code in the browser window (waiting up to 90s)…")
            
            # STRATEGY 1: Primary selector - #pane-side
            try:
                page.wait_for_selector('#pane-side', timeout=90_000)
                _log("✅ Primary chat list selector found (#pane-side)")
            except PWTimeout:
                # STRATEGY 2: Fallback - data-testid="chat-list"
                _log("⚠️ Primary selector failed. Trying alternative...")
                try:
                    page.wait_for_selector('div[data-testid="chat-list"]', timeout=30_000)
                    _log("✅ Alternative chat list selector found (data-testid)")
                except PWTimeout:
                    # STRATEGY 3: Fallback - aria-label
                    _log("⚠️ Second selector failed. Trying third option...")
                    try:
                        page.wait_for_selector('div[aria-label="Chat list"]', timeout=20_000)
                        _log("✅ Third chat list selector found (aria-label)")
                    except PWTimeout:
                        # STRATEGY 4: Last resort - check main app
                        _log("⚠️ All chat list selectors failed. Checking main app...", "ERROR")
                        page.wait_for_selector('#app', timeout=10_000)
                        _log("⚠️ Main app loaded but chat list not detected. Waiting extra time...", "WARNING")
                        time.sleep(8)
        else:
            page.wait_for_selector('#pane-side', timeout=40_000)
        
        # CRITICAL: Wait for chats to fully render
        _log("⏳ Waiting for chats to fully render...")
        time.sleep(5)  # Extended wait for chat rows to appear
        
        # Verify chat containers exist
        chat_count = len(page.query_selector_all(SELECTORS['chat_container']))
        
        if chat_count == 0:
            _log("⚠️ No chat containers detected. Attempting recovery...", "WARNING")
            
            # Try scrolling to trigger lazy loading
            scroll_chat_list(page, "down")
            time.sleep(3)
            
            # Check again
            chat_count = len(page.query_selector_all(SELECTORS['chat_container']))
            
            if chat_count == 0:
                # Try one more scroll
                scroll_chat_list(page, "up")
                time.sleep(3)
                chat_count = len(page.query_selector_all(SELECTORS['chat_container']))
        
        # Final verification with extended wait for headful mode
        if chat_count == 0 and headful:
            _log("⚠️ Chats still not detected. This appears to be a WhatsApp Web loading issue.", "ERROR")
            _log("💡 MANUAL INTERVENTION REQUIRED:", "INFO")
            _log("   Please WAIT in the browser window for 30 seconds...")
            _log("   The bot will keep checking for chats to appear.")
            _log("   If you see chats in the browser, they should be detected soon.")
            
            # Wait up to 30 seconds while checking every 5 seconds
            for i in range(6):  # 6 attempts × 5 seconds = 30 seconds
                time.sleep(5)
                # Try multiple selectors to detect chats
                chats = (
                    page.query_selector_all(SELECTORS['chat_container']) or 
                    page.query_selector_all(SELECTORS['chat_container_alt']) or
                    page.query_selector_all('div[role="listitem"]') or
                    page.query_selector_all('div[data-testid="cell-frame-container"]')
                )
                chat_count = len(chats)
                if chat_count > 0:
                    _log(f"✅ Chats detected after waiting! Found {chat_count} chats.")
                    break
                _log(f"   ⏳ Still waiting... (attempt {i+1}/6)")
        
        # Final result
        if chat_count > 0:
            _log(f"✅ WhatsApp Web is ready. Found {chat_count} chats.")
            return True
        else:
            _log("❌ Still no chats detected after all recovery attempts.", "ERROR")
            _log("💡 This is likely a WhatsApp Web issue. Try these steps:", "INFO")
            _log("   1. Keep the browser window OPEN and WAIT 30-60 seconds")
            _log("   2. Press F5 to manually refresh when WhatsApp Web fully loads")
            _log("   3. Check your internet connection speed")
            _log("   4. Ensure WhatsApp mobile app is connected to internet")
            _log("   5. If using WiFi, try switching to mobile data or vice versa")
            _log("   6. Close and reopen WhatsApp on your phone")
            return False
        
    except PWTimeout:
        _log("QR code not scanned in time. Run with --headful to log in.", "ERROR")
        raise
    except Exception as e:
        _log(f"Error loading WhatsApp Web: {e}", "ERROR")
        return False


def scroll_chat_list(page, direction: str = "down"):
    """Scroll the chat list container to load more chats."""
    try:
        chat_pane = page.query_selector(SELECTORS['chat_list'])
        if chat_pane:
            if direction == "down":
                page.evaluate("element => element.scrollBy(0, 300)", chat_pane)
                _log("📜 Scrolled chat list down")
            else:
                page.evaluate("element => element.scrollBy(0, -300)", chat_pane)
                _log("📜 Scrolled chat list up")
            page.wait_for_timeout(500)  # Wait for scroll to complete
            return True
    except Exception as e:
        _log(f"Scroll failed: {e}", "WARNING")
    return False


def get_unread_chat_elements(page):
    """Return list of chat row elements with robust multi-selector strategy."""
    for attempt in range(MAX_RETRIES):
        try:
            # Get the chat list container first
            _log(f"  🔍 Attempt {attempt + 1}/{MAX_RETRIES}: Detecting chat list...")
            
            try:
                chat_list = page.locator("#pane-side")
                if not chat_list.count():
                    _log("  ⚠️ Chat list container (#pane-side) not found", "WARNING")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        scroll_chat_list(page, "down")
                    continue
                _log("  ✅ Chat list container found (#pane-side)")
            except Exception as e:
                _log(f"  ❌ Error finding chat list: {e}", "ERROR")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return []
            
            # STRATEGY 1: Primary selector - div[aria-label][role="listitem"] (FIX 1)
            _log("  🔍 Trying Strategy 1: div[aria-label][role='listitem'] (PRIMARY 2025)")
            all_rows = chat_list.locator("div[aria-label][role='listitem']").all()
            
            # FILTER for unread badges within the rows
            unread_rows = []
            for row in all_rows:
                try:
                    # Check for unread badge icons or aria-labels
                    has_unread = row.evaluate("""(el) => {
                        const sel = '[data-testid="icon-unread-count"], span[aria-label*="unread"], span[aria-label*="new message"]';
                        return !!el.querySelector(sel);
                    }""")
                    if has_unread:
                        unread_rows.append(row)
                except:
                    continue

            if unread_rows:
                _log(f"  ✅ Strategy 1 SUCCESS! Found {len(unread_rows)} unread chat(s) [ARIA-LABEL 2025]")
                return unread_rows
            
            # STRATEGY 2: Fallback - detect unread dots/badges specifically
            _log("  🔍 Trying Strategy 2: [data-testid='icon-unread-count']")
            badges = chat_list.locator('[data-testid="icon-unread-count"]').all()
            if badges:
                unread_rows = []
                for b in badges:
                    try:
                        # Find the ancestor row/container
                        row = b.locator("xpath=ancestor::div[@role='listitem']").first
                        if row.count() == 0:
                            row = b.locator("xpath=ancestor::div[@data-testid='cell-frame-container']").first
                        if row.count() > 0:
                            unread_rows.append(row)
                    except:
                        continue
                if unread_rows:
                    _log(f"  ✅ Strategy 2 SUCCESS! Found {len(unread_rows)} unread chat(s)")
                    return unread_rows
            
            # STRATEGY 3: Fallback - data-testid (OLD but still works sometimes)
            _log("  🔍 Trying Strategy 3: div[data-testid='cell-frame-container'] (LEGACY)")
            rows = chat_list.locator("div[data-testid='cell-frame-container']").all()
            
            if len(rows) > 0:
                _log(f"  ✅ Strategy 3 SUCCESS! Found {len(rows)} chat(s) [LEGACY SELECTOR]")
                return rows
            
            # STRATEGY 4: Fallback - CSS class ._ak72
            _log("  🔍 Trying Strategy 4: div._ak72 (CSS CLASS)")
            rows = chat_list.locator("div._ak72").all()
            
            if len(rows) > 0:
                _log(f"  ✅ Strategy 4 SUCCESS! Found {len(rows)} chat(s)")
                return rows
            
            # All strategies failed
            _log("  ⚠️ No chats found with any selector. Scrolling and retrying...", "WARNING")
            
            if attempt < MAX_RETRIES - 1:
                scroll_chat_list(page, "down")
                time.sleep(RETRY_DELAY)
                scroll_chat_list(page, "up")
                time.sleep(RETRY_DELAY)
                
        except Exception as e:
            _log(f"  ❌ Error detecting chats (attempt {attempt + 1}): {e}", "ERROR")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    _log("❌ No chats detected after all attempts", "ERROR")
    return []


def get_sender_name(chat_element) -> str:
    """Extract the display name from a chat row element with multiple fallbacks (FIX 2)."""
    try:
        # STRATEGY 1: Primary - data-testid="cell-frame-title" span
        name_el = chat_element.query_selector('div[data-testid="cell-frame-title"] span')
        if name_el and name_el.inner_text().strip():
            return name_el.inner_text().strip()
        
        # STRATEGY 2: Fallback - span[title]
        name_el = chat_element.query_selector('span[title]')
        if name_el and name_el.inner_text().strip():
            return name_el.inner_text().strip()
        
        # STRATEGY 3: Fallback - span[dir="auto"]
        name_el = chat_element.query_selector('span[dir="auto"]')
        if name_el and name_el.inner_text().strip():
            return name_el.inner_text().strip()
            
    except Exception as e:
        _log(f"  ⚠️ Error extracting sender name: {e}", "WARNING")
    
    return "Unknown Contact"


def open_chat_with_retry(page, chat_element, sender_name: str):
    """Open a chat with robust scroll-into-view, hover, and click retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            _log(f"  🚪 Opening chat: {sender_name} (attempt {attempt + 1}/{MAX_RETRIES})")
            
            # Step 1: Scroll into view
            try:
                chat_element.scroll_into_view_if_needed(timeout=5000)
                page.wait_for_timeout(300)
                _log("     ✅ Scrolled chat into view")
            except Exception as e:
                _log(f"     ⚠️ Scroll failed: {e}", "WARNING")
            
            # Step 2: Hover to activate
            try:
                chat_element.hover(timeout=5000)
                page.wait_for_timeout(200)
                _log("     ✅ Hovered over chat")
            except Exception as e:
                _log(f"     ⚠️ Hover failed: {e}", "WARNING")
            
            # Step 3: Click with force option
            chat_element.click(force=True, timeout=5000)
            page.wait_for_timeout(CHAT_OPEN_MS)
            
            _log(f"  ✅ Chat opened successfully: {sender_name}")
            return True
            
        except Exception as e:
            _log(f"  ❌ Chat click attempt {attempt + 1}/{MAX_RETRIES} failed: {e}", "WARNING")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                # Try scrolling again on retry
                try:
                    chat_element.scroll_into_view_if_needed()
                    time.sleep(0.5)
                except:
                    pass
    
    _log(f"  ❌ Failed to open chat after {MAX_RETRIES} attempts", "ERROR")
    return False


def get_recent_messages(page, max_msgs: int = MAX_MESSAGES) -> list[str]:
    """Read ONLY incoming customer messages with robust detection."""
    try:
        _log("  ⏳ Waiting for messages to load...")
        
        # Wait for messages to fully render (CRITICAL)
        page.wait_for_timeout(3000)
        
        # Ensure we're in a chat by checking message container
        message_list = None
        containers_to_try = [
            SELECTORS['message_list_container'],
            SELECTORS['message_list_alt'],
            SELECTORS['message_list_alt2'],
            SELECTORS['message_container']
        ]
        
        for sel in containers_to_try:
            try:
                message_list = page.wait_for_selector(sel, timeout=5_000)
                if message_list:
                    _log(f"  ✅ Message container detected: {sel}")
                    break
            except:
                continue
        
        if not message_list:
            _log("  ⚠️ Message area not clearly detected, but continuing with general search", "WARNING")
            # Optional: Capture DOM snippet for debug
            try:
                content = page.evaluate("() => document.querySelector('#main').innerHTML.substring(0, 1000)")
                _log(f"  🔬 [DEBUG] #main DOM: {content}")
            except:
                pass
        
        messages = []
        
        # ════════════════════════════════════════════════════════
        # STRATEGY 1: Primary - span.selectable-text (ALL messages)
        # ════════════════════════════════════════════════════════
        _log("  🔍 Strategy 1: span.selectable-text (all messages)")
        try:
            all_selectable = page.locator("span.selectable-text").all()
            all_texts = [el.inner_text() for el in all_selectable if el.inner_text().strip()]
            
            if all_texts:
                messages = all_texts
                _log(f"  ✅ Strategy 1 SUCCESS! Found {len(messages)} message(s)")
        except Exception as e:
            _log(f"  ⚠️ Strategy 1 failed: {e}", "WARNING")
        
        # ════════════════════════════════════════════════════════
        # STRATEGY 2: Fallback - div.copyable-text wrapper
        # ════════════════════════════════════════════════════════
        if not messages:
            _log("  🔍 Strategy 2: div.copyable-text wrapper")
            try:
                copyable_divs = page.locator("div.copyable-text").all()
                copyable_texts = []
                
                for div in copyable_divs:
                    try:
                        span = div.locator("span.selectable-text").first
                        text = span.inner_text()
                        if text.strip():
                            copyable_texts.append(text.strip())
                    except:
                        pass
                
                if copyable_texts:
                    messages = copyable_texts
                    _log(f"  ✅ Strategy 2 SUCCESS! Found {len(messages)} message(s)")
            except Exception as e:
                _log(f"  ⚠️ Strategy 2 failed: {e}", "WARNING")
        
        # ════════════════════════════════════════════════════════
        # STRATEGY 3: Incoming messages ONLY (message-in container)
        # ════════════════════════════════════════════════════════
        if not messages:
            _log("  🔍 Strategy 3: div.message-in (incoming customer messages only)")
            try:
                incoming_divs = page.locator("div.message-in").all()
                incoming_texts = []
                
                for msg_div in incoming_divs:
                    try:
                        text_span = msg_div.locator("span.selectable-text").first
                        text = text_span.inner_text()
                        if text.strip():
                            incoming_texts.append(text.strip())
                    except:
                        pass
                
                if incoming_texts:
                    messages = incoming_texts
                    _log(f"  ✅ Strategy 3 SUCCESS! Found {len(incoming_texts)} INCOMING message(s)")
            except Exception as e:
                _log(f"  ⚠️ Strategy 3 failed: {e}", "WARNING")
        
        # ════════════════════════════════════════════════════════
        # DEBUG: If still no messages, inspect page structure
        # ════════════════════════════════════════════════════════
        if not messages:
            _log("  ❌ No messages found with any strategy", "ERROR")
            _log("  🔬 Debugging page structure...", "DEBUG")
            
            try:
                debug_info = page.evaluate('''() => {
                    return {
                        hasMsgContainer: !!document.querySelector('div[data-testid="msg-container"]'),
                        selectableCount: document.querySelectorAll('span.selectable-text').length,
                        copyableCount: document.querySelectorAll('div.copyable-text').length,
                        messageInCount: document.querySelectorAll('div.message-in').length,
                        messageOutCount: document.querySelectorAll('div.message-out').length
                    };
                }''')
                
                _log(f"  🔬 Page Structure: {debug_info}", "DEBUG")
            except Exception as e:
                _log(f"  ⚠️ Debug inspection failed: {e}", "WARNING")
            
            return []
        
        # Get latest N messages (most recent first)
        latest_messages = messages[-max_msgs:]
        _log(f"  📖 Successfully read {len(latest_messages)} message(s)")
        
        if latest_messages:
            _log(f"  📋 Latest message preview: '{latest_messages[0][:50]}...'")
        
        return latest_messages
        
    except Exception as e:
        _log(f"  ❌ Could not read messages: {e}", "ERROR")
        return []


def type_and_send(page, text: str) -> bool:
    """Type a reply in the input box and click Send with fallback selectors (FIX 3)."""
    try:
        # Wait for footer input box with longer timeout
        _log("  ⏳ Looking for message input box...")
        
        # STRATEGY 1: Primary - data-testid="conversation-compose-box-input"
        box = page.wait_for_selector('div[data-testid="conversation-compose-box-input"]', timeout=DEFAULT_TIMEOUT)
        
        # STRATEGY 2: Fallback - footer div[contenteditable="true"]
        if not box:
            _log("  🔍 Trying fallback selector: footer div[contenteditable='true']")
            box = page.wait_for_selector('footer div[contenteditable="true"]', timeout=15_000)
        
        if not box:
            _log("  ❌ Input box not found", "ERROR")
            return False
            
        _log("  ✅ Input box found, clicking...")
        box.click()
        time.sleep(0.3)

        # Type line by line (newlines via Shift+Enter)
        _log(f"  ⌨️ Typing reply ({len(text)} characters)...")
        lines = text.split("\n")
        for i, line in enumerate(lines):
            # Human-like typing delay - varies based on line length
            typing_delay = max(SEND_DELAY_MS // max(len(line), 1), 30)  # Min 30ms per char
            box.type(line, delay=typing_delay)
            if i < len(lines) - 1:
                box.press("Shift+Enter")
                time.sleep(0.2)  # Small pause between paragraphs

        # Click send button with fallback
        _log("  📤 Clicking send button...")
        
        # STRATEGY 1: Primary - button[data-testid="send"]
        send_btn = page.wait_for_selector('button[data-testid="send"]', timeout=5_000)
        
        # STRATEGY 2: Fallback - button[data-testid="compose-btn-send"]
        if not send_btn:
            _log("  🔍 Trying fallback send button: button[data-testid='compose-btn-send']")
            send_btn = page.wait_for_selector('button[data-testid="compose-btn-send"]', timeout=3_000)
        
        if send_btn:
            send_btn.click()
            page.wait_for_timeout(AFTER_SEND_MS)
            _log("  ✅ Reply sent successfully!")
            return True
        else:
            _log("  ❌ Send button not found", "ERROR")
            return False

    except Exception as e:
        _log(f"  ❌ Failed to send reply: {e}", "ERROR")
        return False


def go_back_to_chat_list(page):
    """Navigate back to the chat list (mobile-style back button or ESC)."""
    try:
        back_btn = page.query_selector(SELECTORS['back_button'])
        if back_btn:
            back_btn.click()
            _log("🔙 Clicked back button")
        else:
            page.keyboard.press("Escape")
            _log("🔙 Pressed Escape key")
        page.wait_for_timeout(800)
        _log("✅ Back to chat list")
    except Exception as e:
        _log(f"Failed to go back: {e}", "WARNING")


# ─────────────────────────────────────────────────────────────────────────────
#  Core Processing Loop
# ─────────────────────────────────────────────────────────────────────────────

def process_unread_chats(page, headful: bool) -> list[str]:
    """
    Iterate over all unread chats, classify each, reply, and log.

    Returns a list of Plan.md table rows (one per chat processed).
    """
    plan_rows      = []
    unread_elements = get_unread_chat_elements(page)

    if not unread_elements:
        _log("No unread chats found in this scan.")
        return plan_rows

    _log(f"🔥 Found {len(unread_elements)} unread chat(s). Processing…")

    for idx, chat_el in enumerate(unread_elements):
        sender = "Unknown"
        try:
            # ── 1. Open the chat ─────────────────────────────────────
            sender = get_sender_name(chat_el)
            _log(f"━━━ [{idx+1}] Opening chat: {sender}")
            
            if not open_chat_with_retry(page, chat_el, sender):
                _log(f"  ⚠️ Failed to open chat. Skipping.", "WARNING")
                go_back_to_chat_list(page)
                continue
            
            page.wait_for_timeout(CHAT_OPEN_MS)

            # ── 2. Read messages ──────────────────────────────────────
            messages = get_recent_messages(page)
            if not messages:
                _log(f"  ⚠️ No readable messages in chat with {sender}. Skipping.", "WARNING")
                go_back_to_chat_list(page)
                continue

            _log(f"  Last message: {messages[-1][:50]}...")

            # ── 3. Classify ───────────────────────────────────────────
            category    = classify(sender, messages)
            hot         = is_hot_lead(messages)
            sens        = is_sensitive(messages)

            _log(
                f"  📊 Category: {category}"
                f"{'  🔥 HOT LEAD' if hot else ''}"
                f"{'  🔒 SENSITIVE' if sens else ''}"
            )

            # ── 4. Generate reply ─────────────────────────────────────
            _log(f"  🤖 Generating AI reply...")
            reply = generate_reply(category, sender, messages, template_seed=idx)
            _log(f"  ✅ Reply generated ({len(reply)} chars)")

            # ── 5. Human approval gate for sensitive content ──────────
            approved = True
            if sens:
                _log("  ⚠️  Sensitive content detected – requesting human approval…", "WARNING")
                approved = request_human_approval(sender, reply)

            # ── 6. Send reply (if approved) ───────────────────────────
            sent = False
            if approved:
                _log(f"  📤 Sending reply to {sender}…")
                sent = type_and_send(page, reply)
                if sent:
                    _log("  ✅ Reply sent successfully.")
                else:
                    _log("  ❌ Reply send failed.", "ERROR")
            else:
                _log("  ⛔ Reply skipped (human declined).", "WARNING")

            # ── 7. Log conversation ───────────────────────────────────
            log_conversation(
                sender_name = sender,
                category    = category,
                messages    = messages,
                reply_sent  = reply,
                hot         = hot,
                sensitive   = sens,
                approved    = approved and sent,
            )

            # ── 8. Plan.md row ────────────────────────────────────────
            plan_rows.append(
                f"| {idx+1} | {sender} | {category} "
                f"| {'🔥' if hot else '—'} "
                f"| {'🔒' if sens else '—'} "
                f"| {'✅' if (approved and sent) else '⛔'} |"
            )

        except Exception as e:
            _log(f"  💥 Unexpected error processing chat {sender}: {e}", "ERROR")
            traceback.print_exc()
            plan_rows.append(f"| {idx+1} | {sender} | ERROR | — | — | ❌ |")

        finally:
            go_back_to_chat_list(page)
            time.sleep(1)

    return plan_rows


# ─────────────────────────────────────────────────────────────────────────────
#  Main Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="WhatsApp Business Agent – Digital FTE"
    )
    parser.add_argument(
        "--loop", action="store_true",
        help="Keep running and re-scan after each cycle.",
    )
    parser.add_argument(
        "--interval", type=int, default=120,
        help="Seconds between scan cycles when --loop is set (default: 120).",
    )
    parser.add_argument(
        "--headful", action="store_true",
        help="Show browser window (needed for first-time QR code scan).",
    )
    return parser.parse_args()


def main():
    args          = parse_args()
    session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_plan_rows = []

    _log("=" * 60)
    _log("  WhatsApp Business Agent – Digital FTE")
    _log(f"  Mode: {'HEADFUL' if args.headful else 'HEADLESS'}"
         f"  |  Loop: {args.loop}"
         f"  |  Interval: {args.interval}s")
    _log(f"  Session started: {session_start}")
    _log("=" * 60)

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        # ── Launch persistent browser context (saves login session) ──
        try:
            browser = pw.chromium.launch_persistent_context(
                user_data_dir = str(SESSION_DIR),
                headless      = not args.headful,
                channel       = "chrome",  # Use installed Chrome instead of bundled
                args          = [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-software-rasterizer",
                    "--enable-features=NetworkService,NetworkServiceInProcess",
                    "--disable-web-security",  # Helps with iframe/shadow DOM rendering
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
                ignore_default_args=["--enable-automation"],
            )
        except Exception as e:
            _log(f"Failed to launch with Chrome, trying Chromium... {e}", "WARNING")
            # Fallback to bundled Chromium if Chrome fails
            browser = pw.chromium.launch_persistent_context(
                user_data_dir = str(SESSION_DIR),
                headless      = not args.headful,
                args          = [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-software-rasterizer",
                    "--enable-features=NetworkService,NetworkServiceInProcess",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )

        page = browser.pages[0] if browser.pages else browser.new_page()

        # Set a realistic viewport and user-agent
        page.set_viewport_size({"width": 1280, "height": 900})
        
        # Add anti-detection script
        try:
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        except Exception as e:
            _log(f"Warning: Could not inject anti-detection: {e}", "WARNING")

        try:
            _log(f"Navigating to {WA_URL}…")
            page.goto(WA_URL, wait_until="domcontentloaded", timeout=60_000)
            
            # Wait for page to fully load
            _log("⏳ Waiting for page to fully load...")
            page.wait_for_load_state("networkidle", timeout=30_000)
            time.sleep(2)  # Extra buffer

            if not wait_for_wa_ready(page, args.headful):
                _log("Failed to load WhatsApp Web properly. Exiting.", "ERROR")
                return
            
            time.sleep(SCAN_DELAY_S)

            cycle = 0
            while True:
                cycle += 1
                _log(f"\n──── SCAN CYCLE #{cycle} ────")

                rows = process_unread_chats(page, args.headful)
                all_plan_rows.extend(rows)

                write_plan(session_start, all_plan_rows)
                _log(f"  Plan.md updated ({len(all_plan_rows)} total chats logged).")

                if not args.loop:
                    _log("Single-pass complete. Exiting (use --loop to keep running).")
                    break

                _log(f"  Sleeping {args.interval}s before next scan…")
                time.sleep(args.interval)

        except KeyboardInterrupt:
            _log("Interrupted by user. Shutting down gracefully…", "WARNING")
        except PWTimeout as e:
            _log(f"Playwright timeout: {e}", "ERROR")
        except Exception as e:
            _log(f"Fatal error: {e}", "ERROR")
            traceback.print_exc()
        finally:
            write_plan(session_start, all_plan_rows)
            browser.close()
            _log("Browser closed. Session saved.")
            _log("=" * 60)


if __name__ == "__main__":
    main()
