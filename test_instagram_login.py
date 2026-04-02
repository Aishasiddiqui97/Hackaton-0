"""
Test Instagram Login - Autonomous Browser Login
This will open a browser and automatically login to Instagram
"""

import sys
import os
from pathlib import Path

# Add AI_Employee_Vault to path
vault_path = Path(__file__).parent / "AI_Employee_Vault"
sys.path.insert(0, str(vault_path))

from instagram.session_manager import InstagramSessionManager
from playwright.sync_api import sync_playwright

def test_login():
    """Test autonomous Instagram login"""
    print("=" * 70)
    print("INSTAGRAM AUTONOMOUS LOGIN TEST")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Open a Chrome browser window")
    print("  2. Navigate to Instagram login page")
    print("  3. Automatically fill in your credentials")
    print("  4. Click the login button")
    print("  5. Handle any popups")
    print("  6. Save session for future use")
    print()
    print("=" * 70)
    print()

    manager = InstagramSessionManager()

    with sync_playwright() as p:
        # Launch browser (NOT headless so you can see it)
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='Asia/Karachi'
        )

        # Add stealth JavaScript to avoid detection
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            window.chrome = {
                runtime: {}
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        page = context.new_page()

        try:
            # Perform autonomous login
            manager.ensure_logged_in(page, context)

            print()
            print("=" * 70)
            print("[SUCCESS] LOGIN SUCCESSFUL!")
            print("=" * 70)
            print()
            print("The browser will stay open for 15 seconds so you can see the result.")
            print("Session has been saved and will be reused next time.")
            print()

            # Keep browser open for 15 seconds
            page.wait_for_timeout(15000)

            return True

        except Exception as e:
            print()
            print("=" * 70)
            print("[FAILED] LOGIN FAILED")
            print("=" * 70)
            print(f"Error: {e}")
            print()
            print("Check the screenshot in AI_Employee_Vault/Logs/ folder")
            print("Check the signal file in AI_Employee_Vault/Signals/ folder")
            print()

            # Keep browser open for 20 seconds so you can see what happened
            page.wait_for_timeout(20000)

            return False

        finally:
            browser.close()

if __name__ == "__main__":
    success = test_login()

    if success:
        print("Next steps:")
        print("  - Run instagram_actions.py to post photos")
        print("  - Run instagram_watcher.py to monitor comments/DMs")
        print("  - Session is saved, no need to login again!")
    else:
        print("Troubleshooting:")
        print("  1. Check your credentials in .env file")
        print("  2. Check if Instagram is showing CAPTCHA")
        print("  3. Try logging in manually first in a regular browser")
        print("  4. Check the screenshot and signal files for details")
