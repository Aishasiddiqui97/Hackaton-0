#!/usr/bin/env python3
"""
Test script for Twitter Browser Automation
Verifies browser automation setup and credentials
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.twitter_browser_server import TwitterBrowserAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_browser_initialization():
    """Test browser can be initialized."""
    print("Testing browser initialization...")

    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')

    if not email or not password:
        print("[FAIL] Twitter credentials not found in .env")
        print("   Add TWITTER_EMAIL and TWITTER_PASSWORD to .env file")
        return False

    agent = TwitterBrowserAgent(email, password)

    try:
        if agent.start_browser():
            print("[PASS] Browser initialized successfully")
            agent.close_browser()
            return True
        else:
            print("[FAIL] Browser initialization failed")
            return False
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_tweet_generation():
    """Test tweet content generation."""
    print("\nTesting tweet generation...")

    email = os.getenv('TWITTER_EMAIL', 'test@example.com')
    password = os.getenv('TWITTER_PASSWORD', 'test')

    agent = TwitterBrowserAgent(email, password)

    try:
        tweet = agent.generate_tweet()

        if len(tweet) <= 280:
            print(f"✅ PASS: Tweet generated ({len(tweet)} chars)")
            print(f"   Preview: {tweet[:100]}...")
            return True
        else:
            print(f"❌ FAIL: Tweet too long ({len(tweet)} chars)")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False


def test_vault_structure():
    """Test vault folder structure exists."""
    print("\nTesting vault structure...")

    required_paths = [
        Path("AI_Employee_Vault/Agents"),
        Path("AI_Employee_Vault/Plans"),
        Path("AI_Employee_Vault/Logs")
    ]

    all_exist = True
    for path in required_paths:
        if path.exists():
            print(f"[PASS] {path} exists")
        else:
            print(f"[FAIL] {path} missing")
            all_exist = False

    return all_exist


def test_log_file():
    """Test log file can be written."""
    print("\nTesting log file...")

    log_file = Path("AI_Employee_Vault/Logs/Twitter_Log.md")

    try:
        if log_file.exists():
            print(f"[PASS] Log file exists at {log_file}")
            return True
        else:
            print(f"[FAIL] Log file not found at {log_file}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False


def test_playwright_installation():
    """Test Playwright is installed."""
    print("\nTesting Playwright installation...")

    try:
        from playwright.sync_api import sync_playwright
        print("[PASS] Playwright is installed")
        return True
    except ImportError:
        print("[FAIL] Playwright not installed")
        print("   Run: pip install playwright")
        print("   Then: playwright install chromium")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("  Twitter Browser Automation - Test Suite")
    print("=" * 60)

    tests = [
        ("Playwright Installation", test_playwright_installation),
        ("Vault Structure", test_vault_structure),
        ("Log File", test_log_file),
        ("Tweet Generation", test_tweet_generation),
        ("Browser Initialization", test_browser_initialization)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} - {str(e)}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] Twitter browser automation is ready.")
        print("\nNext steps:")
        print("1. Add Twitter credentials to .env file")
        print("2. Run: python scripts/test_twitter_post.py")
        print("3. Create task in Inbox to trigger posting")
    else:
        print("\n[WARNING] Some tests failed. Please fix issues before proceeding.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
