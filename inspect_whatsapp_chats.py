"""
Manual Chat Inspector - Check what's actually in your WhatsApp
This helps debug why chats aren't being detected
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def main():
    print("=" * 70)
    print("WHATSAPP CHAT INSPECTOR")
    print("=" * 70)
    print("\nThis will show you EXACTLY what's in your WhatsApp chat list\n")
    
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
            
            print("⏳ Waiting for chat list to load (90 seconds max)...")
            page.wait_for_selector('#pane-side', timeout=90000)
            print("✅ Chat list loaded!\n")
            
            # Wait a moment for everything to render
            time.sleep(2)
            
            # Inspect all chats
            print("=" * 70)
            print("INSPECTING ALL CHATS IN YOUR LIST")
            print("=" * 70 + "\n")
            
            all_chats = page.query_selector_all('div[data-testid="cell-frame-container"]')
            print(f"📊 Total chats found: {len(all_chats)}\n")
            
            for i, chat in enumerate(all_chats[:15], 1):  # Show first 15 chats
                try:
                    # Get chat name
                    name_el = chat.query_selector('span[data-testid="cell-frame-title"]')
                    name = name_el.inner_text().strip() if name_el else "Unknown"
                    
                    # Check for unread badge
                    unread_badge = chat.query_selector('[data-testid="icon-unread-count"]')
                    has_unread = "✅ YES" if unread_badge else "❌ NO"
                    
                    # Get timestamp
                    time_el = chat.query_selector('span[data-testid="cell-frame-timestamp"]')
                    timestamp = time_el.inner_text().strip() if time_el else "N/A"
                    
                    # Get last message preview
                    msg_el = chat.query_selector('span.selectable-text')
                    last_msg = msg_el.inner_text().strip()[:30] if msg_el else "N/A"
                    
                    print(f"{i}. {name}")
                    print(f"   Unread: {has_unread}")
                    print(f"   Time: {timestamp}")
                    print(f"   Last: {last_msg}...")
                    print()
                    
                except Exception as e:
                    print(f"{i}. Error reading chat: {e}\n")
            
            print("=" * 70)
            print("INSTRUCTIONS:")
            print("=" * 70)
            print("1. Look at the list above")
            print("2. Find a chat that says 'Unread: ✅ YES'")
            print("3. OR find a chat with recent timestamp (now, 1m, 2m, etc.)")
            print("4. Manually click on that chat in the browser")
            print("5. Then close this script and run the bot again")
            print("=" * 70 + "\n")
            
            input("Press Enter when you've inspected the chats...")
            
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
