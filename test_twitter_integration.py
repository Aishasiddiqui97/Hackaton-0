#!/usr/bin/env python3
"""
Quick test script for Twitter MCP Server
Tests login and posting functionality
"""

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:3006"

def test_health():
    """Test server health"""
    print("\n[1/4] Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Server is running: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_login():
    """Test login"""
    print("\n[2/4] Testing login...")
    try:
        username = os.getenv('TWITTER_USERNAME')
        password = os.getenv('TWITTER_PASSWORD')
        twofa = os.getenv('TWITTER_2FA_SECRET', '')

        if not username or not password:
            print("❌ TWITTER_USERNAME or TWITTER_PASSWORD not set in .env")
            return False

        payload = {
            "username": username,
            "password": password
        }

        if twofa:
            payload["twoFactorSecret"] = twofa

        response = requests.post(f"{BASE_URL}/login", json=payload, timeout=120)
        result = response.json()

        if result.get('success'):
            print(f"✅ Login successful: {result.get('message')}")
            return True
        else:
            print(f"❌ Login failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_post_tweet():
    """Test posting a tweet"""
    print("\n[3/4] Testing tweet post...")
    try:
        tweet_text = "Testing autonomous Twitter integration from Gold Tier Digital FTE! 🤖 #AI #Automation"

        response = requests.post(
            f"{BASE_URL}/post_tweet",
            json={"text": tweet_text},
            timeout=60
        )
        result = response.json()

        if result.get('success'):
            print(f"✅ Tweet posted successfully!")
            print(f"   URL: {result.get('tweetUrl', 'Not captured')}")
            return True
        else:
            print(f"❌ Tweet failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Post error: {e}")
        return False

def test_mentions():
    """Test getting mentions"""
    print("\n[4/4] Testing mentions check...")
    try:
        response = requests.get(f"{BASE_URL}/mentions", timeout=30)
        result = response.json()

        if result.get('success'):
            print(f"✅ Mentions retrieved: {result.get('mentionsCount', 0)} mentions")
            return True
        else:
            print(f"❌ Mentions failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Mentions error: {e}")
        return False

def main():
    print("=" * 60)
    print("Twitter MCP Server Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Health Check", test_health()))

    if results[0][1]:  # Only continue if server is running
        results.append(("Login", test_login()))

        if results[1][1]:  # Only continue if login succeeded
            results.append(("Post Tweet", test_post_tweet()))
            results.append(("Check Mentions", test_mentions()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! Twitter integration is working perfectly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("   - Make sure the MCP server is running: node mcp_servers/twitter_mcp.js")
        print("   - Check your .env credentials")
        print("   - Review logs: AI_Employee_Vault/Logs/Twitter_Log.md")

if __name__ == "__main__":
    main()
