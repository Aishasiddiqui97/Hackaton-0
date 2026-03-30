#!/usr/bin/env python3
"""
Twitter Browser Post Test
Executes a real tweet post using browser automation
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.twitter_browser_server import TwitterMCPServer

# Load environment variables
load_dotenv()


def main():
    """Execute autonomous Twitter post."""
    print("=" * 60)
    print("  Twitter Browser Automation - Live Post Test")
    print("=" * 60)

    # Get credentials
    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')

    if not email or not password:
        print("\n[ERROR] ERROR: Twitter credentials not found")
        print("\nPlease add to .env file:")
        print("TWITTER_EMAIL=your_email@example.com")
        print("TWITTER_PASSWORD=your_password")
        return False

    print(f"\n Email: {email}")
    print(" Password: [HIDDEN]")

    # Confirm before posting
    print("\n[WARNING]  WARNING: This will post a REAL tweet to your account!")
    response = input("\nContinue? (yes/no): ")

    if response.lower() != 'yes':
        print("\n[ERROR] Cancelled by user")
        return False

    print("\n[STARTING] Starting autonomous Twitter posting...")
    print("This may take 2-3 minutes...\n")

    # Initialize server
    server = TwitterMCPServer(email, password)

    # Execute autonomous post
    result = server.autonomous_post()

    print("\n" + "=" * 60)
    print("  Result")
    print("=" * 60)

    if result['success']:
        print("\n[SUCCESS] SUCCESS! Tweet posted successfully")
        print(f"\n Content: {result['tweet_content'][:100]}...")
        print(f"\n URL: {result['tweet_url']}")
        print(f"\n Log saved to: AI_Employee_Vault/Logs/Twitter_Log.md")
        return True
    else:
        print(f"\n[ERROR] FAILED: {result.get('error', 'Unknown error')}")
        print("\nCheck logs/twitter_browser_actions.log for details")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
