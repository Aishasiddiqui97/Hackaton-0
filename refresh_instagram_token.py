#!/usr/bin/env python3
"""
Instagram Token Refresh Tool
Exchanges short-lived token for long-lived token (60 days)
"""

import requests
import sys
import json
from datetime import datetime, timedelta

def exchange_token(short_lived_token, app_id, app_secret):
    """Exchange short-lived token for long-lived token"""
    url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }

    print("[*] Exchanging short-lived token for long-lived token...")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        long_lived_token = data.get("access_token")
        expires_in = data.get("expires_in", 5184000)  # Default 60 days

        expiry_date = datetime.now() + timedelta(seconds=expires_in)

        print("[+] SUCCESS! Long-lived token generated")
        print(f"[*] Expires: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[*] Valid for: {expires_in // 86400} days")
        print("\n" + "="*60)
        print("YOUR NEW TOKEN:")
        print("="*60)
        print(long_lived_token)
        print("="*60)

        return long_lived_token
    else:
        print(f"[-] ERROR: {response.status_code}")
        print(response.json())
        return None

def get_instagram_account_id(access_token, page_id):
    """Get Instagram Business Account ID from Facebook Page"""
    url = f"https://graph.facebook.com/v21.0/{page_id}"
    params = {
        "fields": "instagram_business_account",
        "access_token": access_token
    }

    print(f"\n[*] Getting Instagram Account ID for Page {page_id}...")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        ig_account = data.get("instagram_business_account")
        if ig_account:
            ig_id = ig_account.get("id")
            print(f"[+] Instagram Business Account ID: {ig_id}")
            return ig_id
        else:
            print("[-] No Instagram Business Account linked to this page")
            print("   Make sure your Instagram is:")
            print("   1. Converted to Business/Creator account")
            print("   2. Connected to your Facebook Page")
            return None
    else:
        print(f"[-] ERROR: {response.status_code}")
        print(response.json())
        return None

def verify_token_permissions(access_token):
    """Check what permissions the token has"""
    url = "https://graph.facebook.com/v21.0/me/permissions"
    params = {"access_token": access_token}

    print("\n[*] Checking token permissions...")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        granted = [p["permission"] for p in data.get("data", []) if p["status"] == "granted"]

        required = [
            "instagram_basic",
            "instagram_content_publish",
            "instagram_manage_comments",
            "pages_read_engagement"
        ]

        print("[+] Granted permissions:")
        for perm in granted:
            if "instagram" in perm or "pages" in perm:
                print(f"   [+] {perm}")

        missing = [r for r in required if r not in granted]
        if missing:
            print("\n[!] Missing recommended permissions:")
            for perm in missing:
                print(f"   [-] {perm}")

        return granted
    else:
        print(f"[-] ERROR: {response.status_code}")
        return []

def main():
    print("="*60)
    print("Instagram Token Refresh Tool")
    print("="*60)

    # Get inputs
    if len(sys.argv) >= 4:
        short_token = sys.argv[1]
        app_id = sys.argv[2]
        app_secret = sys.argv[3]
        page_id = sys.argv[4] if len(sys.argv) > 4 else "122101694919274206"
    else:
        print("\nUsage:")
        print("  python refresh_instagram_token.py <SHORT_TOKEN> <APP_ID> <APP_SECRET> [PAGE_ID]")
        print("\nOr run interactively:")
        short_token = input("\nPaste your short-lived token: ").strip()
        app_id = input("Enter your Facebook App ID: ").strip()
        app_secret = input("Enter your Facebook App Secret: ").strip()
        page_id = input(f"Enter your Facebook Page ID [122101694919274206]: ").strip() or "122101694919274206"

    # Exchange token
    long_token = exchange_token(short_token, app_id, app_secret)

    if long_token:
        # Verify permissions
        verify_token_permissions(long_token)

        # Get Instagram Account ID
        ig_id = get_instagram_account_id(long_token, page_id)

        # Generate .env update
        print("\n" + "="*60)
        print("UPDATE YOUR .env FILE:")
        print("="*60)
        print(f"FACEBOOK_ACCESS_TOKEN={long_token}")
        print(f"INSTAGRAM_ACCESS_TOKEN={long_token}")
        if ig_id:
            print(f"INSTAGRAM_ACCOUNT_ID={ig_id}")
        print("="*60)

        # Save to file
        with open("instagram_tokens.txt", "w") as f:
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"FACEBOOK_ACCESS_TOKEN={long_token}\n")
            f.write(f"INSTAGRAM_ACCESS_TOKEN={long_token}\n")
            if ig_id:
                f.write(f"INSTAGRAM_ACCOUNT_ID={ig_id}\n")

        print("\n[+] Tokens saved to: instagram_tokens.txt")
        print("\n[!] IMPORTANT: Update your .env file with these values!")
    else:
        print("\n[-] Failed to generate long-lived token")
        sys.exit(1)

if __name__ == "__main__":
    main()
