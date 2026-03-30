#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visual test - shows browser and waits for you to see each step
"""

import requests
import time
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3006"

def main():
    print("=" * 60)
    print("Visual Browser Test")
    print("=" * 60)
    print()
    print("This test will:")
    print("1. Check if server is running")
    print("2. Wait for you to see the browser")
    print("3. Post a test tweet")
    print("4. Show you each step")
    print()
    print("=" * 60)
    print()

    # Check server
    print("[1/3] Checking server...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        result = response.json()
        print(f"✅ Server running on port {result['port']}")
        print(f"   Logged in: {result['loggedIn']}")
        print(f"   Agent initialized: {result.get('agentInitialized', False)}")
        print()

        if not result['loggedIn']:
            print("⚠️  Not logged in yet!")
            print("   The server should be logging in now.")
            print("   Check the server terminal and browser window.")
            print()
            print("   Waiting 30 seconds for login to complete...")
            time.sleep(30)

            # Check again
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            result = response.json()
            if not result['loggedIn']:
                print("❌ Still not logged in after 30 seconds")
                print("   Check server terminal for errors")
                return
            else:
                print("✅ Login completed!")
                print()

    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        print("   Start it: .\\start_twitter_autonomous.bat")
        return

    # Post tweet
    print("[2/3] Posting test tweet...")
    print()
    print("WATCH THE BROWSER WINDOW NOW!")
    print("You should see:")
    print("  - Browser navigates to Twitter home")
    print("  - Clicks the compose button")
    print("  - Types the tweet")
    print("  - Clicks Post")
    print()
    input("Press Enter when you're ready to watch...")
    print()

    tweet_text = "🤖 Visual test successful! Browser automation working perfectly. #AI #Automation"

    try:
        print(f"Posting: {tweet_text[:50]}...")
        print()
        print("👀 WATCH THE BROWSER NOW!")
        print()

        response = requests.post(
            f"{BASE_URL}/post_tweet",
            json={"text": tweet_text},
            timeout=60
        )
        result = response.json()

        if result.get('success'):
            print()
            print("✅ Tweet posted successfully!")
            print(f"   URL: {result.get('tweetUrl', 'Not captured')}")
            print()
        else:
            print()
            print(f"❌ Tweet failed: {result.get('error')}")
            print()
            print("Check:")
            print("  - Did you see the browser window?")
            print("  - Check debug_before_post.png for screenshot")
            print("  - Check server terminal for detailed logs")
            print()

    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()

    # Summary
    print("[3/3] Summary")
    print("=" * 60)
    print()
    print("Did you see the browser window?")
    print("  YES → Everything is working!")
    print("  NO  → Run: .\\fix_browser_visibility.bat")
    print()
    print("Check these files:")
    print("  - debug_before_post.png (screenshot)")
    print("  - AI_Employee_Vault/Logs/Twitter_Log.md (logs)")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
