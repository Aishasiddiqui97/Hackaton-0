"""
Simple Manual WhatsApp Test - Opens WhatsApp and waits for YOU to verify it's working
This bypasses all automation to check if WhatsApp Web itself is functional
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def main():
    print("=" * 70)
    print("SIMPLE WHATSAPP WEB TEST - NO AUTOMATION")
    print("=" * 70)
    print("\nThis will just open WhatsApp Web and let YOU verify it works.\n")
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})
        
        try:
            print("📍 Opening WhatsApp Web...")
            page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
            
            print("\n" + "=" * 70)
            print("INSTRUCTIONS FOR YOU:")
            print("=" * 70)
            print("1. Wait for WhatsApp Web to fully load in the browser")
            print("2. If you see QR code:")
            print("   → Scan it with your phone")
            print("   → Settings > Linked Devices > Link a Device")
            print("3. Once logged in, you should see your chat list")
            print("4. CLICK on any chat to open it")
            print("5. Verify you can see messages in that chat")
            print("6. Come back to terminal and press Enter")
            print("=" * 70)
            print("\n⏳ Waiting for you to verify WhatsApp Web is working...\n")
            
            input("Press Enter when you've verified WhatsApp Web is working...")
            
            # Now test if we can detect what you see
            print("\n🔍 Checking what the bot can detect...")
            
            # Check chat list
            chat_list = page.query_selector('#pane-side')
            print(f"Chat list (#pane-side): {'✅ FOUND' if chat_list else '❌ NOT FOUND'}")
            
            # Count chats
            chats = page.query_selector_all('div[data-testid="cell-frame-container"]')
            print(f"Chat containers found: {len(chats)}")
            
            # Check if a chat is open
            msg_container = page.query_selector('div[data-testid="msg-container"]')
            print(f"Message container: {'✅ OPEN CHAT DETECTED' if msg_container else 'ℹ️ No chat currently open'}")
            
            # Check for messages
            if msg_container:
                messages = page.query_selector_all('span.selectable-text')
                print(f"Messages in current chat: {len(messages)}")
                
                if messages:
                    last_msg = messages[-1].inner_text().strip()
                    print(f"Latest message: '{last_msg[:50]}...'")
            
            print("\n" + "=" * 70)
            print("DIAGNOSIS:")
            print("=" * 70)
            
            if not chat_list:
                print("❌ PROBLEM: Chat list not detected")
                print("   CAUSE: WhatsApp Web hasn't loaded properly")
                print("   FIX: Press F5 to refresh, wait for chat list to appear")
            elif len(chats) == 0:
                print("❌ PROBLEM: No chats detected")
                print("   CAUSE: Either no chats exist or WhatsApp is still loading")
                print("   FIX: Wait longer or scroll down in the chat list")
            elif not msg_container:
                print("✅ GOOD: WhatsApp Web is working!")
                print("ℹ️ INFO: No chat is currently open")
                print("   ACTION: Click on a chat in the browser, then run the bot again")
            else:
                print("✅ EXCELLENT: Everything is working perfectly!")
                print(f"   - Chat list: Loaded ({len(chats)} chats)")
                print(f"   - Messages: {len(messages)} found")
                print("\n🎉 You can now run the autonomous bot!")
            
            print("\n" + "=" * 70)
            print("\nNext steps:")
            print("1. If you saw ✅ above, run: python whatsapp_agent.py --headful --loop")
            print("2. If you saw ❌ above, fix the issue first (refresh/wait)")
            print("3. Keep this browser open - session is saved for future runs\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print("\n💡 Browser will remain open. Close manually when done.")
            input("Press Enter to exit...")
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
