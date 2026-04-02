#!/usr/bin/env python3
"""
Test script for Twitter Browser Automation - Chrome Profile Edition
Verifies browser automation setup with real Chrome profile
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
    """Test browser can be initialized with Chrome profile."""
    print("Testing browser initialization...")

    agent = TwitterBrowserAgent()

    try:
        if agent.start_browser():
            print("[PASS] Browser initialized successfully with Chrome profile")
            agent.close_browser()
            return True
        else:
            print("[FAIL] Browser initialization failed")
            return False
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_login_check():
    """Test login status check."""
    print("\nTesting login status check...")

    agent = TwitterBrowserAgent()

    try:
        if not agent.start_browser():
            print("[FAIL] Could not start browser")
            return False

        if agent.check_login():
            print("[PASS] Login check successful - you are logged in")
            agent.close_browser()
            return True
        else:
            print("[FAIL] Not logged in - please log in manually in Chrome first")
            agent.close_browser()
            return False
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        agent.close_browser()
        return False


def test_tweet_generation():
    """Test tweet content generation."""
    print("\nTesting tweet generation...")

    agent = TwitterBrowserAgent()

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
        Path("AI_Employee_Vault/twitter"),
        Path("AI_Employee_Vault/Logs"),
        Path("AI_Employee_Vault/Signals")
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
            print(f"[INFO] Log file will be created on first post")
            return True
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


def test_chrome_profile():
    """Test Chrome profile path exists."""
    print("\nTesting Chrome profile...")

    chrome_data_dir = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
    chrome_profile = os.getenv("CHROME_PROFILE", "Default")

    profile_path = Path(chrome_data_dir) / chrome_profile

    if profile_path.exists():
        print(f"[PASS] Chrome profile exists at {profile_path}")
        return True
    else:
        print(f"[FAIL] Chrome profile not found at {profile_path}")
        print("   Check CHROME_USER_DATA_DIR in .env")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("  Twitter Browser Automation - Test Suite")
    print("  Chrome Profile Edition")
    print("=" * 60)

    tests = [
        ("Playwright Installation", test_playwright_installation),
        ("Chrome Profile Path", test_chrome_profile),
        ("Vault Structure", test_vault_structure),
        ("Log File", test_log_file),
        ("Tweet Generation", test_tweet_generation),
        ("Browser Initialization", test_browser_initialization),
        ("Login Status Check", test_login_check)
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
        print("1. Make sure you're logged into Twitter in Chrome")
        print("2. Run: python test_twitter_session.py")
        print("3. Run: python test_twitter_dry_run.py")
        print("4. Test real posting with: python playwright_twitter.py --dry-run")
    else:
        print("\n[WARNING] Some tests failed. Please fix issues before proceeding.")
        print("\nCommon fixes:")
        print("- If 'Login Status Check' failed: Log into Twitter manually in Chrome")
        print("- If 'Chrome Profile Path' failed: Update CHROME_USER_DATA_DIR in .env")
        print("- If 'Playwright Installation' failed: Run 'pip install playwright && playwright install chromium'")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
