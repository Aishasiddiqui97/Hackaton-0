#!/usr/bin/env python3
"""
Facebook Page Access Token Fixer
----------------------------------
Exchanges your User Access Token for a Page Access Token,
then updates .env automatically so posting works.

Valid permissions for v18+ Graph API:
  - pages_manage_posts
  - pages_read_engagement
  (manage_pages / pages_show_list are DEPRECATED and will error)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import requests
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
PAGE_ID    = os.getenv('FACEBOOK_PAGE_ID')
API_VER    = 'v18.0'


def get_page_access_token(user_token, page_id):
    """Exchange user token for page-specific access token via /me/accounts."""
    print(f"\n🔄 Fetching Page Access Token for page ID: {page_id}")
    url = f"https://graph.facebook.com/{API_VER}/me/accounts"
    params = {'access_token': user_token}

    resp = requests.get(url, params=params, timeout=15)
    data = resp.json()

    if resp.status_code != 200 or 'error' in data:
        err = data.get('error', {})
        print(f"❌ API Error [{err.get('code','?')}]: {err.get('message', data)}")
        print_token_help()
        return None

    pages = data.get('data', [])
    if not pages:
        print("❌ No pages returned. The token lacks 'pages_manage_posts' permission.")
        print_token_help()
        return None

    print(f"\n📋 Found {len(pages)} page(s):")
    for page in pages:
        marker = " ◀ MATCH" if page['id'] == page_id else ""
        print(f"   • {page['name']}  (ID: {page['id']}){marker}")

    # Find exact match by page_id
    matched = next((p for p in pages if p['id'] == page_id), pages[0])
    if matched['id'] != page_id:
        print(f"\n⚠️  Page ID {page_id} not found; using: {matched['name']} ({matched['id']})")

    return matched['access_token'], matched['id'], matched['name']


def update_env_file(page_token, page_id):
    """Write the new Page Access Token and Page ID back into .env."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    updated_token = False
    updated_id    = False

    for line in lines:
        if line.startswith('FACEBOOK_ACCESS_TOKEN='):
            new_lines.append(f'FACEBOOK_ACCESS_TOKEN={page_token}\n')
            updated_token = True
        elif line.startswith('FACEBOOK_PAGE_ID='):
            new_lines.append(f'FACEBOOK_PAGE_ID={page_id}\n')
            updated_id = True
        # Also update Instagram token if it was the same as the old FB token
        elif line.startswith('INSTAGRAM_ACCESS_TOKEN=') and line.strip().split('=', 1)[1] == USER_TOKEN:
            new_lines.append(f'INSTAGRAM_ACCESS_TOKEN={page_token}\n')
        else:
            new_lines.append(line)

    if not updated_token:
        new_lines.append(f'FACEBOOK_ACCESS_TOKEN={page_token}\n')
    if not updated_id:
        new_lines.append(f'FACEBOOK_PAGE_ID={page_id}\n')

    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\n✅ .env updated!")
    print(f"   FACEBOOK_ACCESS_TOKEN = {page_token[:30]}...")
    print(f"   FACEBOOK_PAGE_ID      = {page_id}")


def test_post(page_token, page_id):
    """Send a real test post to confirm the token works."""
    print("\n🧪 Sending test post...")
    url = f"https://graph.facebook.com/{API_VER}/{page_id}/feed"
    payload = {
        'message': '🤖 Token verified — autonomous system online!',
        'access_token': page_token
    }
    resp = requests.post(url, data=payload, timeout=30)

    if resp.status_code == 200:
        post_id = resp.json().get('id', 'unknown')
        print(f"✅ Test post successful! Post ID: {post_id}")
        return True
    else:
        err = resp.json().get('error', {})
        print(f"❌ Test post failed: {err.get('message', resp.text)}")
        return False


def print_token_help():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HOW TO GET A VALID PAGE ACCESS TOKEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 1. Open: https://developers.facebook.com/tools/explorer/
 2. Select your App from the top-right dropdown
 3. Click "Generate Access Token"
 4. Add ONLY these two permissions:
      ✅ pages_manage_posts
      ✅ pages_read_engagement
    (do NOT add manage_pages or pages_show_list — they are deprecated)
 5. Click "Generate Token" and copy it
 6. Paste it into .env as FACEBOOK_ACCESS_TOKEN=<paste here>
 7. Run this script again: python get_page_token.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


if __name__ == '__main__':
    print("=" * 56)
    print("🔧  Facebook Page Access Token Fixer")
    print("=" * 56)

    if not USER_TOKEN or not PAGE_ID:
        print("❌ Missing FACEBOOK_ACCESS_TOKEN or FACEBOOK_PAGE_ID in .env")
        sys.exit(1)

    print(f"📄 Page ID    : {PAGE_ID}")
    print(f"🔑 Token start: {USER_TOKEN[:20]}...")

    result = get_page_access_token(USER_TOKEN, PAGE_ID)

    if not result:
        sys.exit(1)

    page_token, real_page_id, page_name = result
    print(f"\n✅ Got Page Token for: {page_name} ({real_page_id})")

    update_env_file(page_token, real_page_id)

    print("\n" + "=" * 56)
    try:
        choice = input("🤔 Run a test post now? (y/n): ").strip().lower()
    except EOFError:
        choice = 'n'

    if choice == 'y':
        test_post(page_token, real_page_id)

    print("\n✅ All done!  Now run:  .\\test_facebook_api.bat")
    print("=" * 56)
