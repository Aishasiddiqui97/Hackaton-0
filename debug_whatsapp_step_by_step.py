"""
Debug WhatsApp Agent - Step by Step Testing
This script tests each component individually to find exactly where the issue is.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def log(msg, icon="ℹ️"):
    print(f"{icon} {msg}")

def test_whatsapp_step_by_step():
    """Test WhatsApp automation step by step with detailed debugging."""
    
    print("\n" + "=" * 70)
    print("WHATSAPP DEBUG TEST - STEP BY STEP")
    print("=" * 70 + "\n")
    
    with sync_playwright() as pw:
        # Launch browser
        log("Launching browser...", "🚀")
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        try:
            # STEP 1: Navigate to WhatsApp
            log("STEP 1: Navigate to WhatsApp Web", "📍")
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
            log("✅ Navigation successful", "✓")
            
            # Wait a bit for page to initialize
            time.sleep(2)
            
            # Check if already logged in or need QR
            log("Checking login status...", "🔍")
            chat_list = page.query_selector('div[data-testid="chat-list"]')
            qr_code = page.query_selector('[data-testid="qr"]')
            
            if chat_list:
                log("Already logged in! Chat list found.", "✅")
            elif qr_code:
                log("QR code detected! Please scan with WhatsApp mobile app.", "📱")
                log("Waiting up to 90 seconds for QR scan...", "⏳")
                
                # Wait for chat list after QR scan
                page.wait_for_selector('div[data-testid="chat-list"]', timeout=90000)
                log("✅ QR scanned successfully! Chat list loaded.", "✓")
            else:
                log("Page loaded but chat list not visible yet. Waiting...", "⏳")
            
            # STEP 2: Wait for chat list (final check)
            log("STEP 2: Final chat list verification...", "📍")
            page.wait_for_selector('div[data-testid="chat-list"]', timeout=30000)
            log("✅ Chat list confirmed loaded", "✓")
            
            # STEP 3: Check for unread chats
            log("STEP 3: Scanning for unread chats...", "📍")
            unread_chats = page.query_selector_all(
                'div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])'
            )
            
            if not unread_chats:
                log("Trying fallback selector...", "⚠️")
                unread_chats = page.query_selector_all(
                    '//span[@data-testid="icon-unread-count"]/ancestor::div[@data-testid="cell-frame-container"]'
                )
            
            log(f"Found {len(unread_chats)} unread chat(s)", "✓" if unread_chats else "⚠️")
            
            if not unread_chats:
                log("No unread chats found. Please send a message to test with.", "💡")
                input("Press Enter when you have an unread chat...")
                unread_chats = page.query_selector_all(
                    'div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])'
                )
            
            if not unread_chats:
                log("Still no unread chats. Test cannot continue.", "❌")
                return
            
            # STEP 4: Open first unread chat
            log("STEP 4: Opening first unread chat...", "📍")
            sender_name = "Unknown"
            try:
                name_el = unread_chats[0].query_selector('span[data-testid="cell-frame-title"]')
                if name_el:
                    sender_name = name_el.inner_text().strip()
                log(f"Chat name detected: {sender_name}", "✓")
            except:
                pass
            
            unread_chats[0].click()
            page.wait_for_timeout(3000)
            log("✅ Chat opened", "✓")
            
            # STEP 5: Read messages
            log("STEP 5: Reading messages...", "📍")
            try:
                page.wait_for_selector('div[data-testid="msg-container"]', timeout=5000)
                log("Message container found", "✓")
                
                messages = page.query_selector_all('span.selectable-text')
                log(f"Found {len(messages)} message bubble(s)", "✓")
                
                if messages:
                    last_msg = messages[-1].inner_text().strip()
                    log(f"Last message: '{last_msg[:50]}...'", "✓")
                else:
                    log("No messages found!", "❌")
            except Exception as e:
                log(f"Failed to read messages: {e}", "❌")
            
            # STEP 6: Find input box
            log("STEP 6: Looking for input box...", "📍")
            try:
                input_box = page.wait_for_selector('footer div[contenteditable="true"]', timeout=10000)
                if input_box:
                    log("✅ Input box found in footer!", "✓")
                    
                    # Test typing
                    log("Testing input box (typing 'test')...", "⌨️")
                    input_box.click()
                    time.sleep(0.3)
                    input_box.type("test", delay=50)
                    log("✅ Typing works!", "✓")
                    
                    # Clear the test text
                    input_box.fill("")
                    log("Input cleared", "✓")
                else:
                    log("Input box NOT found!", "❌")
            except Exception as e:
                log(f"Failed to find input box: {e}", "❌")
            
            # STEP 7: Test send button
            log("STEP 7: Checking send button...", "📍")
            try:
                send_btn = page.query_selector('button[data-testid="compose-btn-send"]')
                if send_btn:
                    log("✅ Send button exists", "✓")
                else:
                    log("Send button NOT found!", "❌")
            except Exception as e:
                log(f"Error checking send button: {e}", "❌")
            
            # STEP 8: Go back
            log("STEP 8: Going back to chat list...", "📍")
            try:
                back_btn = page.query_selector('button[data-testid="back"]')
                if back_btn:
                    back_btn.click()
                    log("Clicked back button", "✓")
                else:
                    page.keyboard.press("Escape")
                    log("Pressed Escape key", "✓")
                time.sleep(1)
                log("✅ Back to chat list", "✓")
            except Exception as e:
                log(f"Failed to go back: {e}", "❌")
            
            print("\n" + "=" * 70)
            log("DEBUG TEST COMPLETE!", "🎉")
            print("=" * 70)
            print("\nResults Summary:")
            print("  ✓ WhatsApp loaded successfully")
            print(f"  ✓ Unread chats detected: {len(unread_chats) > 0}")
            print(f"  ✓ Chat opened: True")
            print(f"  ✓ Messages readable: {len(messages) > 0}")
            print(f"  ✓ Input box found: {input_box is not None}")
            print(f"  ✓ Send button exists: {send_btn is not None}")
            print("\nIf all above are True, the bot should work!")
            print("\nNext step: Run the actual bot")
            print("  python whatsapp_agent.py --headful")
            print("=" * 70 + "\n")
            
        except Exception as e:
            log(f"Test failed with error: {e}", "❌")
            print("\n" + "=" * 70)
            log("TROUBLESHOOTING TIPS:", "💡")
            print("=" * 70)
            print("1. If QR code appeared but wasn't scanned:")
            print("   - Open WhatsApp on your phone")
            print("   - Go to Settings > Linked Devices")
            print("   - Tap 'Link a Device'")
            print("   - Scan the QR code on your screen")
            print()
            print("2. If page is blank or stuck:")
            print("   - Refresh the browser manually")
            print("   - Check your internet connection")
            print("   - Wait for WhatsApp to fully load")
            print()
            print("3. If session expired:")
            print("   - Delete the whatsapp_session folder")
            print("   - Run this script again")
            print("   - Re-scan QR code")
            print("=" * 70 + "\n")
            import traceback
            traceback.print_exc()
        
        finally:
            log("Browser will remain open. Close manually when done.", "💡")
            input("Press Enter to exit...")
            browser.close()


if __name__ == "__main__":
    test_whatsapp_step_by_step()
