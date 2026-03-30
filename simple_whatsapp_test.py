"""
Simple WhatsApp Test - Just Open and Wait for Manual QR Scan
This version gives you unlimited time to scan QR code
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def main():
    print("=" * 70)
    print("SIMPLE WHATSAPP TEST - UNLIMITED QR SCAN TIME")
    print("=" * 70)
    print()
    
    with sync_playwright() as pw:
        # Launch browser
        print("🚀 Launching browser...")
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
        
        # Navigate to WhatsApp
        print("📍 Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")
        
        print("\n" + "=" * 70)
        print("📱 INSTRUCTIONS:")
        print("=" * 70)
        print("1. Browser will show WhatsApp Web")
        print("2. If you see QR code:")
        print("   - Open WhatsApp on your phone")
        print("   - Settings > Linked Devices > Link a Device")
        print("   - Scan the QR code on screen")
        print("3. If already logged in, chat list will appear")
        print("4. Once chat list appears, send yourself a test message")
        print("=" * 70)
        print()
        print("⏳ Waiting for you to scan QR code (unlimited time)...")
        print("   Press Ctrl+C when done or if you want to exit")
        print()
        
        # Wait indefinitely for user to scan
        try:
            while True:
                # Check if chat list appeared
                chat_list = page.query_selector('div[data-testid="chat-list"]')
                if chat_list:
                    print("\n✅ Chat list detected!")
                    
                    # Check for unread chats
                    unread = page.query_selector_all(
                        'div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])'
                    )
                    
                    if unread:
                        print(f"🔥 Found {len(unread)} unread chat(s)!")
                        print("\n🎉 SUCCESS! Your WhatsApp is working!")
                        print("\nNow you can run the full bot:")
                        print("  python whatsapp_agent.py --headful")
                        break
                    else:
                        print("ℹ️  No unread chats yet. Send yourself a message from another number to test.")
                        print("\nWaiting for unread chat... (or press Ctrl+C to exit)")
                        
                        # Keep checking for new unread chats
                        for i in range(60):  # Wait 5 more minutes
                            time.sleep(5)
                            unread = page.query_selector_all(
                                'div[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])'
                            )
                            if unread:
                                print(f"\n✅ Unread chat detected! ({len(unread)} chats)")
                                print("\n🎉 Bot is ready to use!")
                                break
                        break
                else:
                    time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        
        print("\n" + "=" * 70)
        print("Test complete. Browser will close in 5 seconds...")
        time.sleep(5)
        browser.close()
        print("✅ Done!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
