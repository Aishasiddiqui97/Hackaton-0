"""
Test Message Reading - Debug Tool
Tests all message reading strategies and shows detailed output
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def log(msg, icon="ℹ️"):
    print(f"{icon} {msg}")

def test_message_reading():
    """Test message reading with all fallback strategies."""
    
    print("\n" + "=" * 70)
    print("MESSAGE READING DEBUG TEST")
    print("=" * 70 + "\n")
    
    with sync_playwright() as pw:
        # Launch browser
        log("Launching browser...", "🚀")
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        try:
            # Navigate to WhatsApp
            log("Navigating to WhatsApp Web...", "📍")
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
            
            # Wait for chat list
            log("Waiting for chat list...", "⏳")
            page.wait_for_selector('#pane-side', timeout=90000)
            log("✅ Chat list loaded!", "✓")
            
            # Check for unread chats
            log("Scanning for unread chats...", "🔍")
            unread_chats = page.query_selector_all(
                'div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])'
            )
            
            if not unread_chats:
                log("No unread chats found. Please open a chat manually.", "⚠️")
                input("Press Enter after you've opened a chat...")
            
            # Open first unread chat or let user do it manually
            if unread_chats:
                log(f"Found {len(unread_chats)} unread chat(s). Opening first one...", "📱")
                
                # Get sender name
                name_el = unread_chats[0].query_selector('span[data-testid="cell-frame-title"]')
                sender_name = name_el.inner_text().strip() if name_el else "Unknown"
                log(f"Opening chat: {sender_name}", "📂")
                
                # Click to open
                unread_chats[0].click()
                log("✅ Chat opened!", "✓")
            
            # WAIT FOR MESSAGES TO LOAD (CRITICAL!)
            log("Waiting 3 seconds for messages to fully load...", "⏳")
            time.sleep(3)
            
            # NOW TEST ALL MESSAGE READING STRATEGIES
            log("=" * 70)
            log("TESTING MESSAGE READING STRATEGIES", "🧪")
            log("=" * 70)
            
            messages_found = []
            
            # STRATEGY 1: span.selectable-text
            log("\nStrategy 1: Testing span.selectable-text...", "🔍")
            try:
                bubbles = page.query_selector_all('span.selectable-text')
                texts = [b.inner_text().strip() for b in bubbles if b.inner_text().strip()]
                log(f"Found {len(texts)} message(s): {texts[:3]}{'...' if len(texts) > 3 else ''}", "✓")
                if texts:
                    messages_found.extend(texts)
            except Exception as e:
                log(f"Failed: {e}", "❌")
            
            # STRATEGY 2: div.copyable-text
            log("\nStrategy 2: Testing div.copyable-text...", "🔍")
            try:
                copyable = page.query_selector_all('div.copyable-text')
                copyable_texts = []
                for cb in copyable:
                    try:
                        text_el = cb.query_selector('span.selectable-text')
                        if text_el:
                            copyable_texts.append(text_el.inner_text().strip())
                    except:
                        pass
                log(f"Found {len(copyable_texts)} message(s): {copyable_texts[:3]}{'...' if len(copyable_texts) > 3 else ''}", "✓")
                if copyable_texts and not messages_found:
                    messages_found.extend(copyable_texts)
            except Exception as e:
                log(f"Failed: {e}", "❌")
            
            # STRATEGY 3: div.message-in (incoming only)
            log("\nStrategy 3: Testing div.message-in (incoming only)...", "🔍")
            try:
                incoming = page.query_selector_all('div.message-in')
                incoming_texts = []
                for im in incoming:
                    try:
                        text_el = im.query_selector('span.selectable-text')
                        if text_el:
                            incoming_texts.append(text_el.inner_text().strip())
                    except:
                        pass
                log(f"Found {len(incoming_texts)} incoming message(s): {incoming_texts[:3]}{'...' if len(incoming_texts) > 3 else ''}", "✓")
                if incoming_texts and not messages_found:
                    messages_found.extend(incoming_texts)
            except Exception as e:
                log(f"Failed: {e}", "❌")
            
            # STRATEGY 4: Count message types
            log("\nStrategy 4: Counting message types...", "🔍")
            try:
                msg_in_count = len(page.query_selector_all('div.message-in'))
                msg_out_count = len(page.query_selector_all('div.message-out'))
                log(f"Incoming (message-in): {msg_in_count}", "ℹ️")
                log(f"Outgoing (message-out): {msg_out_count}", "ℹ️")
            except Exception as e:
                log(f"Failed: {e}", "❌")
            
            # STRATEGY 5: Container text extraction
            log("\nStrategy 5: Testing container text extraction...", "🔍")
            try:
                chat_container = page.query_selector('div[data-testid="chat-container"]')
                if chat_container:
                    all_text = chat_container.inner_text()
                    if all_text:
                        lines = [line.strip() for line in all_text.split('\n') if line.strip() and len(line.strip()) > 5]
                        log(f"Extracted {len(lines)} line(s) from container: {lines[:5]}{'...' if len(lines) > 5 else ''}", "✓")
                        if lines and not messages_found:
                            messages_found.extend(lines[-5:])
            except Exception as e:
                log(f"Failed: {e}", "❌")
            
            # FINAL RESULT
            log("\n" + "=" * 70)
            log("FINAL RESULT", "📊")
            log("=" * 70)
            
            if messages_found:
                log(f"✅ SUCCESS! Found {len(messages_found)} total message(s)", "🎉")
                log("\nLatest messages:", "📋")
                for i, msg in enumerate(messages_found[-5:], max(1, len(messages_found)-4)):
                    log(f"  {i}. {msg}", "💬")
                
                latest_msg = messages_found[-1] if messages_found else None
                if latest_msg:
                    log(f"\n🎯 LATEST CUSTOMER MESSAGE: '{latest_msg}'", "⭐")
            else:
                log("❌ No messages found with any strategy!", "💥")
                log("\nPossible reasons:", "💡")
                log("  1. Chat has no text messages (only images/videos)", "•")
                log("  2. Messages haven't loaded yet (try waiting longer)", "•")
                log("  3. WhatsApp changed their UI structure", "•")
                log("  4. You're looking at your own sent messages, not received", "•")
            
            # PAGE STRUCTURE DEBUG INFO
            log("\n" + "=" * 70)
            log("PAGE STRUCTURE DEBUG INFO", "🔬")
            log("=" * 70)
            
            try:
                page_structure = page.evaluate('''() => {
                    return {
                        url: window.location.href,
                        hasChatContainer: !!document.querySelector('div[data-testid="chat-container"]'),
                        hasMsgContainer: !!document.querySelector('div[data-testid="msg-container"]'),
                        messageInCount: document.querySelectorAll('div.message-in').length,
                        messageOutCount: document.querySelectorAll('div.message-out').length,
                        selectableTextCount: document.querySelectorAll('span.selectable-text').length,
                        copyableTextCount: document.querySelectorAll('div.copyable-text').length
                    };
                }''')
                
                for key, value in page_structure.items():
                    log(f"{key}: {value}", "📍")
                    
            except Exception as e:
                log(f"Debug inspection failed: {e}", "❌")
            
            log("\n" + "=" * 70)
            log("TEST COMPLETE!", "🎉")
            log("=" * 70)
            log("\nNext steps:")
            log("  1. If messages were found, the bot should work!", "✅")
            log("  2. Run: python whatsapp_agent.py --headful", "💡")
            log("  3. Watch the logs to see which strategy succeeds\n", "📋")
            
        except Exception as e:
            log(f"Test failed: {e}", "❌")
            import traceback
            traceback.print_exc()
        
        finally:
            log("Browser will remain open. Close manually when done.", "💡")
            input("Press Enter to exit...")
            browser.close()


if __name__ == "__main__":
    try:
        test_message_reading()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
