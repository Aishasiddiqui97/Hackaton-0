#!/usr/bin/env python3
"""
Get Facebook Page ID from Access Token
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import requests
from dotenv import load_dotenv

load_dotenv()

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')


def get_page_id():
    """Get the correct Page ID from access token"""
    
    if not FACEBOOK_ACCESS_TOKEN:
        print("❌ FACEBOOK_ACCESS_TOKEN not found in .env file")
        return None
    
    print("=" * 60)
    print("🔍 Getting Facebook Page ID")
    print("=" * 60)
    print()
    
    # Get pages managed by this token
    url = 'https://graph.facebook.com/v18.0/me/accounts'
    params = {'access_token': FACEBOOK_ACCESS_TOKEN}
    
    try:
        print("📡 Fetching page information...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            
            if not pages:
                print("❌ No pages found for this token")
                print()
                print("💡 Make sure:")
                print("1. Token is a Page Access Token (not User token)")
                print("2. You have admin access to the page")
                print("3. Token has 'pages_manage_posts' permission")
                return None
            
            print(f"✅ Found {len(pages)} page(s):\n")
            
            for i, page in enumerate(pages, 1):
                page_id = page.get('id')
                page_name = page.get('name')
                access_token = page.get('access_token', 'N/A')
                
                print(f"Page {i}:")
                print(f"  Name: {page_name}")
                print(f"  ID: {page_id}")
                print(f"  Token: {access_token[:30]}...")
                print()
                
                # Update .env file with correct values
                if i == 1:  # Use first page
                    print("=" * 60)
                    print("📝 Add these to your .env file:")
                    print("=" * 60)
                    print(f"FACEBOOK_PAGE_ID={page_id}")
                    print(f"FACEBOOK_ACCESS_TOKEN={access_token}")
                    print()
                    
                    # Try to update .env automatically
                    try:
                        update_env_file(page_id, access_token)
                    except Exception as e:
                        print(f"⚠️ Could not auto-update .env: {e}")
                        print("Please update manually.")
            
            return pages[0].get('id') if pages else None
        
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"❌ Error: {error_msg}")
            print()
            print("💡 Your token might be:")
            print("1. A User Access Token (need Page Access Token)")
            print("2. Expired")
            print("3. Missing permissions")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def update_env_file(page_id, access_token):
    """Update .env file with correct values"""
    
    try:
        # Read current .env
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Update lines
        new_lines = []
        page_id_updated = False
        token_updated = False
        
        for line in lines:
            if line.startswith('FACEBOOK_PAGE_ID='):
                new_lines.append(f'FACEBOOK_PAGE_ID={page_id}\n')
                page_id_updated = True
            elif line.startswith('FACEBOOK_ACCESS_TOKEN='):
                new_lines.append(f'FACEBOOK_ACCESS_TOKEN={access_token}\n')
                token_updated = True
            else:
                new_lines.append(line)
        
        # Add if not found
        if not page_id_updated:
            new_lines.append(f'\nFACEBOOK_PAGE_ID={page_id}\n')
        if not token_updated:
            new_lines.append(f'FACEBOOK_ACCESS_TOKEN={access_token}\n')
        
        # Write back
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("✅ .env file updated automatically!")
        print()
        
    except Exception as e:
        raise e


def test_with_correct_id(page_id, access_token):
    """Test posting with correct credentials"""
    
    print("=" * 60)
    print("🧪 Testing with correct credentials")
    print("=" * 60)
    print()
    
    url = f'https://graph.facebook.com/v18.0/{page_id}/feed'
    
    payload = {
        'message': '🚀 Test post from Graph API!\n\nThis is working! ✅',
        'access_token': access_token
    }
    
    try:
        print("📤 Posting test message...")
        response = requests.post(url, data=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            post_id = data.get('id')
            print(f"✅ SUCCESS! Post ID: {post_id}")
            print()
            print("🎉 Your Facebook posting is now working!")
            return True
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown')
            print(f"❌ Error: {error_msg}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == '__main__':
    page_id = get_page_id()
    
    if page_id:
        print()
        input("Press Enter to test posting with correct credentials...")
        
        # Reload to get updated token
        load_dotenv(override=True)
        new_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        
        test_with_correct_id(page_id, new_token)
    
    print()
    input("Press Enter to exit...")
