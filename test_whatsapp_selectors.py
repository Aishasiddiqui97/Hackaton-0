"""
Test WhatsApp Selectors - Debug Tool
Use this to verify the fixed selectors are working correctly.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def test_selectors():
    """Test all the fixed WhatsApp Web selectors."""
    
    print("=" * 60)
    print("Testing Fixed WhatsApp Web Selectors")
    print("=" * 60)
    
    with sync_playwright() as pw:
        # Launch browser
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,  # Show browser for debugging
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        try:
            # Navigate to WhatsApp
            print("\n1. Navigating to WhatsApp Web...")
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
            
            # Wait for chat list
            print("2. Waiting for chat list to load...")
            page.wait_for_selector('div[data-testid="chat-list"]', timeout=40000)
            print("   ✅ Chat list loaded!")
            
            # Test 1: Unread chats selector
            print("\n3. Testing unread chat selector...")
            # Primary 2025 Strategy
            unread_chats = page.query_selector_all(
                'div[aria-label][role="listitem"]:has([data-testid="icon-unread-count"], [aria-label*="unread"])'
            )
            print(f"   Found {len(unread_chats)} unread chat(s) via Primary (2025)")
            
            if not unread_chats:
                print("   Trying Fallback 1 (data-testid)...")
                unread_chats = page.query_selector_all(
                    'div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])'
                )
                print(f"   Fallback 1 found {len(unread_chats)} unread chat(s)")
            
            if not unread_chats:
                print("   Trying Fallback 2 (XPath ancestor)...")
                unread_chats = page.query_selector_all(
                    '//span[@data-testid="icon-unread-count"]/ancestor::div[@role="listitem"]'
                )
                print(f"   Fallback 2 found {len(unread_chats)} unread chat(s)")
            
            # Test 2: Message input box selector
            print("\n4. Testing message input box selector...")
            if unread_chats:
                print("   Opening first unread chat...")
                unread_chats[0].click()
                page.wait_for_timeout(3000)
                
                # Try multiple message area selectors
                input_box = None
                for sel in ['footer div[contenteditable="true"]', 'div[data-testid="conversation-compose-box-input"]']:
                    input_box = page.query_selector(sel)
                    if input_box:
                        print(f"   ✅ Input box found via: {sel}")
                        break
                
                if not input_box:
                    print("   ❌ No input box found")
                    
                # Test 3: Message bubbles selector with area detection
                print("\n5. Testing message bubble selector...")
                
                message_area = None
                area_selectors = ['#main div[role="application"]', 'div[data-testid="conversation-panel-messages"]', 'div.copyable-area', 'div[data-testid="msg-container"]']
                
                for sel in area_selectors:
                    message_area = page.query_selector(sel)
                    if message_area:
                        print(f"   ✅ Message area found: {sel}")
                        break
                print(f"   Found {len(messages)} message bubble(s)")
                
                if messages:
                    last_msg = messages[-1].inner_text().strip()
                    print(f"   Last message: {last_msg[:50]}...")
                else:
                    print("   ❌ No messages found")
                    
            else:
                print("   No unread chats to test with")
                
            print("\n" + "=" * 60)
            print("Selector Test Complete!")
            print("=" * 60)
            print("\nKeep this browser open and check if:")
            print("  ✓ Unread chats were detected")
            print("  ✓ Chat opened successfully")
            print("  ✓ Messages were read")
            print("  ✓ Input box was found in footer")
            print("\nIf all passed, the main bot should work!")
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            print("\nBrowser will remain open. Close it manually when done.")
            input("Press Enter to close browser...")
            browser.close()


if __name__ == "__main__":
    test_selectors()
