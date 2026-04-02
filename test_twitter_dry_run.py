#!/usr/bin/env python3
"""
Test Twitter Posting in DRY RUN Mode
Tests the full posting flow without actually posting
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add vault to path
sys.path.insert(0, str(Path(__file__).parent / "AI_Employee_Vault" / "twitter"))

from session_manager import TwitterSessionManager
from playwright.sync_api import sync_playwright
import random
import time

CHROME_USER_DATA = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = os.getenv("CHROME_PROFILE", "Default")


def test_twitter_post_dry_run():
    """Test posting a tweet in DRY RUN mode"""

    print("=" * 60)
    print("Twitter/X DRY RUN Test")
    print("=" * 60)
    print()
    print("This will:")
    print("1. Open Chrome with your profile")
    print("2. Check if you're logged in")
    print("3. Open the tweet composer")
    print("4. Fill in test content")
    print("5. NOT actually post (DRY RUN)")
    print()
    print("IMPORTANT: Make sure Chrome is fully closed!")
    print()
    input("Press Enter to continue...")
    print()

    session_manager = TwitterSessionManager()

    with sync_playwright() as p:
        # Launch with real Chrome profile
        profile_path = os.path.join(CHROME_USER_DATA, CHROME_PROFILE)
        print(f"[*] Launching Chrome with profile: {profile_path}")

        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            channel="chrome",
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ],
            viewport={'width': 1366, 'height': 768}
        )

        # Add stealth
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.pages[0] if context.pages else context.new_page()

        try:
            # Check login
            print("\n[STEP 1] Checking login status...")
            if not session_manager.check_login_status(page):
                raise Exception("Not logged in")

            print("\n[STEP 2] Navigating to home...")
            page.goto("https://twitter.com/home", wait_until="networkidle")
            time.sleep(random.uniform(3, 5))

            print("\n[STEP 3] Opening tweet composer...")
            # Random mouse movement
            page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            time.sleep(random.uniform(1.5, 3.5))

            post_button = page.locator('[data-testid="SideNav_NewTweet_Button"]').first
            post_button.click()
            time.sleep(random.uniform(3, 5))

            print("\n[STEP 4] Filling in test content...")
            test_content = f"🧪 DRY RUN TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis is a test tweet that will NOT be posted."

            # Random mouse movement
            page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            time.sleep(random.uniform(1.0, 2.0))

            tweet_input = page.locator('[data-testid="tweetTextarea_0"]').first
            tweet_input.fill(test_content)
            time.sleep(random.uniform(8, 12))

            print("\n[STEP 5] DRY RUN - NOT clicking Post button")
            print(f"\n📄 Test content:\n{test_content}")

            print("\n[*] Waiting 10 seconds so you can see the composer...")
            page.wait_for_timeout(10000)

            print("\n[+] DRY RUN TEST SUCCESSFUL!")
            print("\n✅ Everything works! The automation can:")
            print("   - Use your Chrome profile")
            print("   - Verify you're logged in")
            print("   - Open the tweet composer")
            print("   - Fill in content")
            print("   - Use anti-detection measures")
            print()
            print("🎯 Ready for real posting!")

        except Exception as e:
            print(f"\n[-] DRY RUN TEST FAILED: {e}")
            print("\n[*] Taking screenshot...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"twitter_dry_run_error_{timestamp}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[*] Screenshot saved: {screenshot_path}")
            print("\n[*] Browser will stay open for 15 seconds...")
            page.wait_for_timeout(15000)
            raise

        finally:
            context.close()


if __name__ == "__main__":
    try:
        test_twitter_post_dry_run()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
