#!/usr/bin/env python3
"""
Twitter Login Diagnostic Tool
Shows exactly what's happening with your Chrome profile
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

CHROME_USER_DATA = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = os.getenv("CHROME_PROFILE", "Default")

print("=" * 70)
print("🔍 TWITTER LOGIN DIAGNOSTIC TOOL")
print("=" * 70)
print()

# Step 1: Check Chrome profile exists
profile_path = os.path.join(CHROME_USER_DATA, CHROME_PROFILE)
print(f"[1] Checking Chrome profile path...")
print(f"    Path: {profile_path}")

if os.path.exists(profile_path):
    print(f"    ✅ Profile exists!")
else:
    print(f"    ❌ Profile NOT found!")
    print()
    print("Available profiles:")
    try:
        for item in os.listdir(CHROME_USER_DATA):
            item_path = os.path.join(CHROME_USER_DATA, item)
            if os.path.isdir(item_path) and (item == "Default" or item.startswith("Profile")):
                print(f"    - {item}")
    except:
        print("    Could not list profiles")

    print()
    print("Fix: Update .env file with correct profile name")
    print("Example: CHROME_PROFILE=Profile 1")
    sys.exit(1)

print()

# Step 2: Check if Chrome is running
print("[2] Checking if Chrome is running...")
import subprocess
try:
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    if 'chrome.exe' in result.stdout.lower():
        print("    ⚠️  WARNING: Chrome is running!")
        print("    You MUST close Chrome completely before running this script")
        print()
        print("    To kill Chrome:")
        print("    1. Open Task Manager (Ctrl+Shift+Esc)")
        print("    2. Find all 'Google Chrome' processes")
        print("    3. End all of them")
        print()
        input("Press Enter after closing Chrome...")
    else:
        print("    ✅ Chrome is not running")
except:
    print("    ⚠️  Could not check if Chrome is running")

print()

# Step 3: Launch Chrome and check login
print("[3] Launching Chrome with your profile...")
print("    This will open Chrome - DO NOT CLOSE IT")
print()

with sync_playwright() as p:
    try:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False,
            channel="chrome",
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1366, 'height': 768}
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("[4] Navigating to Twitter...")
        page.goto("https://twitter.com/home", timeout=120000)

        print("[5] Waiting for page to load (30 seconds)...")
        page.wait_for_timeout(30000)

        print()
        print("[6] Checking login status...")
        print()

        # Check multiple indicators
        indicators = {
            '[data-testid="primaryColumn"]': "Home feed column",
            '[data-testid="SideNav_NewTweet_Button"]': "New Tweet button",
            '[aria-label="Home"]': "Home link",
            'a[href="/home"]': "Home navigation",
        }

        found_indicators = []

        for selector, name in indicators.items():
            try:
                if page.locator(selector).is_visible(timeout=3000):
                    print(f"    ✅ Found: {name}")
                    found_indicators.append(name)
                else:
                    print(f"    ❌ Not found: {name}")
            except:
                print(f"    ❌ Not found: {name}")

        print()

        if found_indicators:
            print("=" * 70)
            print("✅ SUCCESS! YOU ARE LOGGED IN!")
            print("=" * 70)
            print()
            print(f"Found {len(found_indicators)} login indicators")
            print()
            print("Your automation will work correctly!")
            print("You can now run: python post_twitter_autonomous.py")
        else:
            print("=" * 70)
            print("❌ NOT LOGGED IN")
            print("=" * 70)
            print()
            print("Current URL:", page.url)
            print()
            print("What to do:")
            print("1. Look at the Chrome window that just opened")
            print("2. If you see a login page, log in NOW")
            print("3. Make sure you check 'Remember me' or 'Stay logged in'")
            print("4. After logging in, close Chrome")
            print("5. Run this diagnostic script again")

        print()
        print("Browser will stay open for 30 seconds so you can see...")
        page.wait_for_timeout(30000)

        context.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("This usually means:")
        print("1. Chrome is still running in background")
        print("2. Network/internet issue")
        print("3. Twitter is blocked/slow")

print()
print("=" * 70)
print("Diagnostic complete")
print("=" * 70)
