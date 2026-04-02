#!/usr/bin/env python3
"""
Test Twitter Session Manager
Verifies that you're logged into Twitter in Chrome
"""

import sys
from pathlib import Path

# Add vault to path
sys.path.insert(0, str(Path(__file__).parent / "AI_Employee_Vault" / "twitter"))

from session_manager import test_session_manager

if __name__ == "__main__":
    print("=" * 60)
    print("Twitter/X Session Test")
    print("=" * 60)
    print()
    print("This will:")
    print("1. Open Chrome with your actual profile")
    print("2. Navigate to Twitter/X")
    print("3. Check if you're logged in")
    print("4. Show you the result")
    print()
    print("IMPORTANT: Make sure Chrome is fully closed before running this!")
    print()
    input("Press Enter to continue...")
    print()

    try:
        test_session_manager()
        print()
        print("=" * 60)
        print("✅ TEST PASSED!")
        print("=" * 60)
        print()
        print("You are logged into Twitter/X in Chrome.")
        print("The automation will work correctly.")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        print("Action required:")
        print("1. Open Chrome browser (not this automation)")
        print("2. Go to https://twitter.com")
        print("3. Log in with your Twitter/X credentials")
        print("4. Complete any security checks")
        print("5. Close Chrome completely")
        print("6. Run this test again")
        print()
