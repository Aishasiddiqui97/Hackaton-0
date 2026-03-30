"""
WhatsApp Autonomous Browser Agent – Direct Runner
==================================================
Fully Autonomous WhatsApp Business Agent using Python and Playwright.
"""

import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("[ERROR] Run: pip install playwright && playwright install chromium")
    sys.exit(1)

from whatsapp_classifier   import classify, is_hot_lead, is_sensitive
from whatsapp_reply_engine import generate_reply, request_human_approval
from whatsapp_logger       import log_conversation

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent
SESSION_DIR = ROOT / "whatsapp_session"
LOGS_DIR    = ROOT / "Logs"
PLANS_DIR   = ROOT / "Plans"
LOG_FILE    = LOGS_DIR / "WhatsApp_Log.md"

SESSION_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
PLANS_DIR.mkdir(exist_ok=True)

WA_URL = "https://web.whatsapp.com"

# ─────────────────────────────────────────────────────────────────────────────

def stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg, level="INFO"):
    line = f"{stamp()} | {level:<8} | {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def append_chat_log(sender, classification, customer_msg, reply_sent, status):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"\n---\n"
            f"**Date:** {stamp()}\n"
            f"**Chat Name:** {sender}\n"
            f"**Customer Message:** {customer_msg}\n"
            f"**Reply Sent:** {reply_sent}\n"
            f"**Status:** {status}\n"
        )

# ─────────────────────────────────────────────────────────────────────────────
#  WhatsApp Helpers
# ─────────────────────────────────────────────────────────────────────────────

def wait_for_login(page, headful):
    log("Waiting for WhatsApp Web to load…")
    timeout = 120_000
    if headful:
        log("👉 SCAN THE QR CODE in the browser window now (120 seconds)…", "WARN")
    
    try:
        page.wait_for_selector('#pane-side', timeout=timeout)
        log("✅  WhatsApp Web ready – chat list loaded.")
        time.sleep(3)
    except PWTimeout:
        log("Timeout waiting for WhatsApp chat list to load.", "ERROR")
        raise


def find_unread_chats(page):
    """Return list of chat row elements that have unread badges."""
    selectors = [
        '[data-testid="icon-unread-count"]',
        'span[data-testid="icon-unread-count"]',
        'div[aria-label*="unread"]',
        'span[aria-label*="unread message"]',
        'span[aria-label*="unread"]'
    ]
    for sel in selectors:
        try:
            elements = page.locator(sel).all()
            if elements:
                return elements
        except Exception:
            continue
    return []


def scroll_chat_list(page):
    """Scroll the #pane-side container to reveal more chats."""
    log("Scrolling chat list down to find more unread chats…")
    try:
        # Detect the correct container explicitly as requested
        chat_list = page.locator("#pane-side")
        if chat_list.count() > 0:
            chat_list.first.evaluate("el => el.scrollTop += 500")
            time.sleep(2)
            return True
        return False
    except Exception as e:
        log(f"Failed to scroll chat list: {e}", "WARN")
        return False


def get_sender_name(page):
    selectors = [
        'header span[data-testid="conversation-info-header-chat-title"]',
        'header span[dir="auto"]',
        'header span.selectable-text',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                return el.inner_text().strip()
        except Exception:
            continue
    return "Unknown Contact"


def open_chat(page, unread_badge):
    """Clicks the parent row of an unread badge with retry logic."""
    for attempt in range(5):
        try:
            # Navigate strictly to the parent chat row to fix icon-click bug
            chat_row = unread_badge.locator("xpath=ancestor::div[@role='row']").first
                
            # Ensure element is visible before clicking (soft attempt)
            try:
                chat_row.scroll_into_view_if_needed(timeout=5_000)
                chat_row.hover(timeout=5_000)
            except Exception:
                pass
            
            # Use force click to bypass any floating overlays
            chat_row.click(force=True, timeout=15_000)
            
            # Wait for message box to appear, guaranteeing chat is open
            page.wait_for_selector("footer div[contenteditable='true']", timeout=30_000)
            return True
        except Exception as e:
            log(f"⚠️ Chat click attempt {attempt+1} failed: {e}", "WARN")
            time.sleep(2)
    return False


def read_last_message(page):
    """Extract the last message text directly."""
    try:
        messages = page.locator("span.selectable-text").all_inner_texts()
        if not messages:
            return ""
            
        last_message = messages[-1].strip()
        return last_message
    except Exception as e:
        log(f"Could not read messages: {e}", "WARN")
        return ""


def send_reply(page, text):
    """Type message in input box and press Enter to send."""
    try:
        # Detect WhatsApp message box with fallback
        box = page.locator('footer div[contenteditable="true"]')
            
        box.click(timeout=15_000)
        time.sleep(0.4)
        
        box.fill(text)
        time.sleep(0.5)
        
        page.keyboard.press("Enter")
        time.sleep(2)
        return True
    except Exception as e:
        log(f"❌ Failed to send reply: {e}", "ERROR")
        return False


def go_back(page):
    try:
        btn = page.query_selector('button[data-testid="back"]')
        if btn:
            btn.click()
        else:
            page.keyboard.press("Escape")
        time.sleep(1)
    except Exception:
        pass


def logout(page):
    log("\nSTEP 9 – Logging out…")
    try:
        # Open WhatsApp menu: button[aria-label="Menu"] or span[data-icon="menu"]
        menu_button = page.locator('button[aria-label="Menu"], span[data-icon="menu"], header div[role="button"][title="Menu"]')
        if menu_button.count() > 0:
            menu_button.first.click(timeout=5_000)
            time.sleep(1)
            
            # Click: Log out
            logout_option = page.locator('div[role="button"]:has-text("Log out"), div[role="button"]:has-text("Logout"), li:has-text("Log out")')
            if logout_option.count() > 0:
                logout_option.first.click()
                time.sleep(1)
                
                # Confirm logout if a dialog appears
                confirm_btn = page.locator('button[data-testid="popup-controls-ok"], div[role="button"]:has-text("Log out")')
                if confirm_btn.count() > 0:
                    confirm_btn.last.click()
                    
                log("✅  Logged out of WhatsApp Web.")
                return True
            else:
                log("⚠️  Logout option not found in menu dropdown.", "WARN")
                return False
        else:
            log("⚠️  Menu button not found.", "WARN")
            return False
    except Exception as e:
        log(f"⚠️  Logout failed: {e}", "WARN")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  Main Loop
# ─────────────────────────────────────────────────────────────────────────────

def process_chats(page):
    """Scan, scroll, and process all unread chats in a loop."""
    results = []
    
    while True:
        unread_badges = find_unread_chats(page)

        if not unread_badges:
            log("No unread chats found currently.")
            # Scroll to find more
            scrolled = scroll_chat_list(page)
            # Re-check after scroll
            unread_badges_after = find_unread_chats(page)
            if not unread_badges_after:
                log("No unread chats remain. Waiting for new messages...")
                time.sleep(5)
                continue # Keep monitoring indefinitely
            else:
                log(f"Found {len(unread_badges_after)} chats after scrolling.")
                unread_badges = unread_badges_after

        # We have unread chats to process
        log(f"Scanning unread chats. Found {len(unread_badges)} in current view.")

        # Process only the first unread chat to avoid stale references if the DOM rearranges
        badge = unread_badges[0]
        sender = "Unknown"
        try:
            log(f"\n──── Processing Chat ────")

            log("Unread chat detected. Opening chat row...")
            if not open_chat(page, badge):
                log("❌ Could not open chat after 3 attempts. Skipping.", "ERROR")
                continue
                
            log("Chat opened successfully.")

            # Read info
            sender = get_sender_name(page)
            log(f"Chat Name: {sender}")

            log("Reading message...")
            msg = read_last_message(page)
            if msg:
                log(f"Customer Message: {msg[:80]}...")
            else:
                log(f"Customer Message: None")

            if not msg:
                log("  No readable message. Skipping.", "WARN")
                go_back(page)
                continue

            log("Generating reply...")
            category = classify(sender, [msg])
            hot      = is_hot_lead([msg])
            sens     = is_sensitive([msg])
            
            log(f"  Classification: {category}"
                f"{'  🔥 HOT' if hot else ''}"
                f"{'  🔒 SENSITIVE' if sens else ''}")

            reply = generate_reply(category, sender, [msg])

            # Gate
            approved = True
            if sens:
                log("  ⚠️  Sensitive content – asking for human approval…", "WARN")
                approved = request_human_approval(sender, reply)

            # Send
            sent = False
            if approved:
                log("Sending reply...")
                sent = send_reply(page, reply)
                if sent:
                    log(f"Reply Sent: {reply}")
            else:
                log("  Reply skipped (human declined).", "WARN")

            # Log
            log("Saving log...")
            status = "Replied" if sent else ("Skipped" if not approved else "Send Failed")
            append_chat_log(sender, category, msg, reply if sent else "N/A", status)

            log_conversation(
                sender_name=sender,
                category=category,
                messages=[msg],
                reply_sent=reply,
                hot=hot,
                sensitive=sens,
                approved=sent,
            )

            results.append({
                "sender": sender,
                "category": category,
                "hot": hot,
                "sensitive": sens,
                "sent": sent,
            })

        except Exception as e:
            log(f"  ERROR processing chat {sender}: {e}", "ERROR")
            traceback.print_exc()
            results.append({"sender": sender, "error": str(e)})
        finally:
            go_back(page)
            time.sleep(2)
                
    return results

def main():
    headful = "--headful" in sys.argv

    if not LOG_FILE.exists():
        LOG_FILE.write_text(
            "# WhatsApp Business Agent – Conversation Log\n\n"
            "_Auto-generated by Digital FTE_\n\n",
            encoding="utf-8",
        )

    log("=" * 58)
    log("  WhatsApp Autonomous Business Agent – LIVE RUN")
    log(f"  Mode: {'HEADFUL (QR scan)' if headful else 'HEADLESS (session)'}")
    log("=" * 58)

    results = []

    with sync_playwright() as pw:
        # Launch persistent browser
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=not headful,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        try:
            log("Opening WhatsApp Web...")
            page.goto(WA_URL, wait_until="domcontentloaded", timeout=60_000)

            wait_for_login(page, headful)

            # Enter loop to scan, scroll, and process chats
            results = process_chats(page)

            # Logout
            logout(page)

        except KeyboardInterrupt:
            log("Interrupted by user.", "WARN")
        except Exception as e:
            log(f"Fatal: {e}", "ERROR")
            traceback.print_exc()
        finally:
            browser.close()
            log("Browser closed. Session saved.")

    # Status summary
    log("\n" + "=" * 58)
    log(f"  SESSION COMPLETE – Processed {len(results)} chat(s)")
    for r in results:
        if "error" in r:
            log(f"  ❌  {r['sender']} → ERROR: {r['error']}", "ERROR")
        else:
            icon = "✅" if r["sent"] else "⛔"
            log(f"  {icon}  [{r['category']}] {r['sender']}")
    log(f"  Log file: {LOG_FILE}")
    log("=" * 58)

    if results:
        print("\nWhatsApp Message Reply Successful")
        print("All conversations logged.")
    else:
        print("\nNo unread messages found after scrolling.")


if __name__ == "__main__":
    main()
