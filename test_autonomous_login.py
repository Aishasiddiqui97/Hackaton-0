#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test autonomous login - waits for server to auto-login, then tests posting
"""

import requests
import time
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3006"

def wait_for_login(max_wait=120):
    """Wait for autonomous login to complete"""
    print("=" * 60)
    print("Autonomous Login Test")
    print("=" * 60)
    print("\nWaiting for server to auto-login...")
    print("(This may take 30-60 seconds on first run)")
    print()

    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            result = response.json()

            if result.get('loggedIn'):
                elapsed = int(time.time() - start_time)
                print(f"\n✅ Auto-login successful! (took {elapsed} seconds)")
                print(f"   Agent initialized: {result.get('agentInitialized')}")
                print(f"   Session dir: {result.get('sessionDir')}")
                return True
            else:
                # Still logging in
                print(".", end="", flush=True)
                time.sleep(2)

        except requests.exceptions.ConnectionError:
            print("\n❌ Server not running!")
            print("   Start server first: .\\start_twitter_autonomous.bat")
            return False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

    print(f"\n⚠️  Timeout after {max_wait} seconds")
    print("   Login may still be in progress - check server terminal")
    return False

def test_post_tweet():
    """Test posting a tweet after auto-login"""
    print("\n" + "=" * 60)
    print("Testing Tweet Post")
    print("=" * 60)

    tweet_text = "🤖 Testing autonomous Twitter integration! This tweet was posted automatically by my Gold Tier Digital FTE. #AI #Automation"

    print(f"\nTweet content: {tweet_text[:50]}...")
    print("\nPosting tweet...")

    try:
        response = requests.post(
            f"{BASE_URL}/post_tweet",
            json={"text": tweet_text},
            timeout=60
        )
        result = response.json()

        if result.get('success'):
            print("\n✅ Tweet posted successfully!")
            print(f"   URL: {result.get('tweetUrl', 'Not captured')}")
            return True
        else:
            print(f"\n❌ Tweet failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ Error posting tweet: {e}")
        return False

def main():
    # Step 1: Wait for auto-login
    if not wait_for_login():
        print("\n" + "=" * 60)
        print("❌ Auto-login test failed")
        print("=" * 60)
        return

    # Step 2: Test posting
    success = test_post_tweet()

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ AUTONOMOUS SYSTEM WORKING PERFECTLY!")
        print("\nWhat just happened:")
        print("1. Server started and auto-logged in")
        print("2. Session was saved to disk")
        print("3. Tweet was posted successfully")
        print("4. Next time: Instant login (no browser)")
        print("\n🎉 Your Twitter integration is fully autonomous!")
    else:
        print("⚠️  Partial success - login worked but posting failed")
        print("Check server logs for details")
    print("=" * 60)

if __name__ == "__main__":
    main()
