#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick MCP connection test - bypasses .env, uses direct credentials
"""

import requests
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:3006"

# Your credentials from .env.template
TWITTER_USERNAME = "@AISHA726035158"
TWITTER_PASSWORD = "Aisha97@"

def test_connection():
    """Test MCP server connection"""
    print("=" * 60)
    print("Twitter MCP Server Connection Test")
    print("=" * 60)

    # Test 1: Health check
    print("\n[1/3] Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        result = response.json()
        print(f"✅ Server is running on port {result['port']}")
        print(f"   Status: {result['status']}")
        print(f"   Logged in: {result['loggedIn']}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        print("\n⚠️  Make sure the MCP server is running:")
        print("   .\\start_twitter_mcp.bat")
        return False

    # Test 2: Login
    print("\n[2/3] Testing login...")
    print(f"   Username: {TWITTER_USERNAME}")
    print(f"   Password: {'*' * len(TWITTER_PASSWORD)}")

    try:
        payload = {
            "username": TWITTER_USERNAME,
            "password": TWITTER_PASSWORD
        }

        print("\n   Sending login request (this may take 30-60 seconds)...")
        print("   Browser will open - watch for 2FA prompt if needed...")

        response = requests.post(
            f"{BASE_URL}/login",
            json=payload,
            timeout=120  # 2 minutes for login
        )
        result = response.json()

        if result.get('success'):
            print(f"\n✅ Login successful!")
            print(f"   Message: {result.get('message')}")
            return True
        else:
            print(f"\n❌ Login failed: {result.get('error')}")
            print("\n   Troubleshooting:")
            print("   1. Check if username is correct (use @username, not email)")
            print("   2. Verify password in .env file")
            print("   3. If 2FA appears, enter code manually in browser")
            print("   4. Check logs: AI_Employee_Vault/Logs/Twitter_Log.md")
            return False

    except requests.exceptions.Timeout:
        print("\n⚠️  Login timed out (this is normal for first run)")
        print("   If browser opened and you see Twitter, login may still succeed")
        print("   Check the MCP server terminal for status")
        return False
    except Exception as e:
        print(f"\n❌ Login error: {e}")
        return False

    # Test 3: Check status after login
    print("\n[3/3] Checking login status...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        result = response.json()

        if result['loggedIn']:
            print("✅ Successfully logged in and connected!")
            print("\n🎉 MCP server is ready to use!")
            print("\nAvailable endpoints:")
            print("   POST /post_tweet - Post a tweet")
            print("   POST /post_with_image - Post with image")
            print("   GET  /mentions - Check mentions")
            print("   POST /logout - Logout")
            return True
        else:
            print("⚠️  Server running but not logged in")
            return False

    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()

    print("\n" + "=" * 60)
    if success:
        print("✅ CONNECTION SUCCESSFUL - MCP server ready!")
        print("\nNext: Try posting a test tweet:")
        print('   curl -X POST http://localhost:3006/post_tweet \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d "{\\"text\\":\\"Test from MCP server!\\"}"')
    else:
        print("⚠️  CONNECTION INCOMPLETE - See errors above")
        print("\nMake sure:")
        print("   1. MCP server is running: .\\start_twitter_mcp.bat")
        print("   2. Credentials are correct in .env")
        print("   3. Browser opens for first-time login")
    print("=" * 60)
