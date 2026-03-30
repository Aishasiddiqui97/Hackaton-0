#!/usr/bin/env python3
"""
Facebook Graph API Poster - Production Ready
Fully autonomous posting using Meta Graph API v18.0
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
GRAPH_API_VERSION = 'v18.0'


def post_to_facebook(message, max_retries=3):
    """
    Post message to Facebook Page using Graph API
    
    Args:
        message (str): Content to post
        max_retries (int): Maximum retry attempts
        
    Returns:
        dict: Response with success status and post_id or error
    """
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        return {
            'success': False,
            'error': 'Missing Facebook credentials in .env file'
        }
    
    url = f'https://graph.facebook.com/{GRAPH_API_VERSION}/{FACEBOOK_PAGE_ID}/feed'
    
    payload = {
        'message': message,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"📤 Posting to Facebook (Attempt {attempt}/{max_retries})...")
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                post_id = data.get('id', 'unknown')
                
                log_success(message, post_id)
                
                print(f"✅ Posted successfully!")
                print(f"📝 Post ID: {post_id}")
                
                return {
                    'success': True,
                    'post_id': post_id,
                    'message': message
                }
            
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                error_code = error_data.get('error', {}).get('code', 'N/A')
                
                print(f"❌ Error {response.status_code}: {error_message} (Code: {error_code})")
                
                if attempt < max_retries:
                    wait_time = attempt * 5
                    print(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    log_failure(message, error_message)
                    return {
                        'success': False,
                        'error': error_message,
                        'error_code': error_code,
                        'status_code': response.status_code
                    }
        
        except requests.exceptions.Timeout:
            print(f"⏱️ Request timeout on attempt {attempt}")
            if attempt < max_retries:
                time.sleep(attempt * 5)
            else:
                log_failure(message, 'Request timeout')
                return {
                    'success': False,
                    'error': 'Request timeout after multiple attempts'
                }
        
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error on attempt {attempt}")
            if attempt < max_retries:
                time.sleep(attempt * 5)
            else:
                log_failure(message, 'Connection error')
                return {
                    'success': False,
                    'error': 'Connection error - check internet'
                }
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            log_failure(message, str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    return {
        'success': False,
        'error': 'Max retries exceeded'
    }


def log_success(message, post_id):
    """Log successful post"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"\n[{timestamp}] ✅ SUCCESS\nPost ID: {post_id}\nMessage: {message[:100]}...\n"
    
    try:
        with open('facebook_posts.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass


def log_failure(message, error):
    """Log failed post"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"\n[{timestamp}] ❌ FAILURE\nError: {error}\nMessage: {message[:100]}...\n"
    
    try:
        with open('facebook_posts.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass


def verify_credentials():
    """Verify Facebook credentials are valid"""
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("❌ Missing credentials!")
        print("Please add to .env file:")
        print("  FACEBOOK_PAGE_ID=your_page_id")
        print("  FACEBOOK_ACCESS_TOKEN=your_token")
        return False
    
    print("✅ Credentials found")
    print(f"📄 Page ID: {FACEBOOK_PAGE_ID}")
    print(f"🔑 Token: {FACEBOOK_ACCESS_TOKEN[:20]}...")
    
    url = f'https://graph.facebook.com/{GRAPH_API_VERSION}/{FACEBOOK_PAGE_ID}'
    params = {'access_token': FACEBOOK_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            page_name = data.get('name', 'Unknown')
            print(f"✅ Connected to page: {page_name}")
            return True
        else:
            print(f"❌ Invalid credentials: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_post():
    """Test posting with sample message"""
    print("=" * 60)
    print("🧪 Facebook Graph API Poster - Test Mode")
    print("=" * 60)
    print()
    
    if not verify_credentials():
        return False
    
    print()
    test_message = f"🚀 Test post from autonomous system!\n\nPosted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n#Automation #Testing"
    
    print(f"📝 Test message:\n{test_message}\n")
    print("-" * 60)
    
    result = post_to_facebook(test_message)
    
    print()
    print("=" * 60)
    if result['success']:
        print("✅ Test successful!")
        print(f"Post ID: {result['post_id']}")
        print("Check your Facebook page to see the post.")
    else:
        print("❌ Test failed!")
        print(f"Error: {result.get('error', 'Unknown')}")
    print("=" * 60)
    
    return result['success']


def post_from_file(filepath):
    """Read content from file and post to Facebook"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        post_content = []
        in_content_section = False
        
        for line in lines:
            if line.strip() == '## Content':
                in_content_section = True
                continue
            elif line.strip().startswith('##') and in_content_section:
                break
            elif in_content_section and line.strip():
                post_content.append(line.strip())
        
        message = '\n\n'.join(post_content)
        
        if not message:
            print("⚠️ No content found in file")
            return False
        
        print(f"📄 Content length: {len(message)} characters")
        
        result = post_to_facebook(message)
        return result['success']
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test_post()
        elif sys.argv[1] == 'verify':
            verify_credentials()
        else:
            filepath = sys.argv[1]
            if Path(filepath).exists():
                post_from_file(filepath)
            else:
                print(f"❌ File not found: {filepath}")
    else:
        test_post()
