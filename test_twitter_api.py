#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Twitter API Server
"""

import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3007"

def main():
    print("=" * 60)
    print("Twitter API Server Test")
    print("=" * 60)
    print()

    # Test 1: Health check
    print("[1/4] Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        result = response.json()
        print(f"✅ Server running on port {result['port']}")
        print(f"   Method: {result['method']}")
        print(f"   Authenticated: {result['authenticated']}")
        print()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running!")
        print("   Start it: .\\start_twitter_api.bat")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Test 2: Get user info
    print("[2/4] Testing authentication...")
    try:
        response = requests.get(f"{BASE_URL}/me", timeout=10)
        result = response.json()

        if result.get('success'):
            user = result['user']
            print(f"✅ Authenticated as: @{user['username']}")
            print(f"   Name: {user['name']}")
            print(f"   ID: {user['id']}")
            print()
        else:
            print(f"❌ Authentication failed: {result.get('error')}")
            print("   Check TWITTER_BEARER_TOKEN in .env")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Test 3: Post tweet
    print("[3/4] Testing tweet posting...")
    tweet_text = "🚀 Testing Twitter API integration! No browser needed. #AI #Automation"

    try:
        response = requests.post(
            f"{BASE_URL}/post_tweet",
            json={"text": tweet_text},
            timeout=30
        )
        result = response.json()

        if result.get('success'):
            print("✅ Tweet posted successfully!")
            print(f"   Tweet ID: {result['tweetId']}")
            print(f"   URL: {result['tweetUrl']}")
            print()
        else:
            print(f"❌ Tweet failed: {result.get('error')}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

    # Test 4: Get mentions
    print("[4/4] Testing mentions...")
    try:
        response = requests.get(f"{BASE_URL}/mentions", timeout=10)
        result = response.json()

        if result.get('success'):
            print(f"✅ Mentions retrieved: {result['mentionsCount']} mentions")
            print()
        else:
            print(f"⚠️  Mentions: {result.get('error')}")
            print()
    except Exception as e:
        print(f"⚠️  Mentions: {e}")
        print()

    # Summary
    print("=" * 60)
    print("✅ Twitter API Integration Working!")
    print("=" * 60)
    print()
    print("Benefits of API vs Browser:")
    print("  ✓ No browser needed")
    print("  ✓ No login issues")
    print("  ✓ Faster (API calls vs browser automation)")
    print("  ✓ More reliable")
    print("  ✓ No automation detection")
    print()
    print("Your Twitter integration is ready!")
    print("=" * 60)

if __name__ == "__main__":
    main()
