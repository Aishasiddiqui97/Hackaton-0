#!/usr/bin/env python3
"""
Twitter/X Poster using Playwright - Chrome Profile Edition
Uses real Chrome profile - NO AUTO-LOGIN
"""

import os
import sys
import time
import random
from pathlib import Path
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Add vault to path for imports
sys.path.insert(0, str(Path(__file__).parent / "AI_Employee_Vault" / "twitter"))
from session_manager import TwitterSessionManager

load_dotenv()

# Chrome profile
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = os.getenv("CHROME_PROFILE", "Default")


class TwitterPosterPlaywright:
    """Twitter/X automation using Playwright with real Chrome profile"""

    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.context = None
        self.page = None
        self.session_manager = TwitterSessionManager()

    def _random_delay(self, min_ms: int = 8000, max_ms: int = 15000):
        """Random human-like delay"""
        delay = random.randint(min_ms, max_ms) / 1000
        time.sleep(delay)

    def _random_mouse_move(self):
        """Random mouse movements"""
        try:
            x = random.randint(100, 500)
            y = random.randint(100, 500)
            self.page.mouse.move(x, y)
            time.sleep(random.uniform(0.1, 0.3))
        except:
            pass

    def start(self):
        """Start browser with real Chrome profile"""
        self.playwright = sync_playwright().start()

        profile_path = os.path.join(CHROME_USER_DATA, CHROME_PROFILE)
        print(f"✅ Using Chrome profile: {profile_path}")

        # Launch persistent context with real Chrome profile
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=self.headless,
            channel="chrome",
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ],
            viewport={'width': 1366, 'height': 768},
            locale='en-US',
            timezone_id='Asia/Karachi'
        )

        # Add stealth JavaScript
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            window.chrome = {
                runtime: {}
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        print("✅ Browser started")

    def check_login(self):
        """Check if already logged in (no auto-login)"""
        try:
            print("🔐 Checking Twitter/X login status...")

            # Use session manager to check login
            is_logged_in = self.session_manager.check_login_status(self.page)

            if is_logged_in:
                print("✅ Already logged in!")
                return True
            else:
                print("❌ Not logged in - please log in manually in Chrome first")
                return False

        except Exception as e:
            print(f"❌ Login check error: {e}")
            return False
    
    def post_tweet(self, content, dry_run=False):
        """Post tweet with anti-detection measures"""
        try:
            print("📝 Creating tweet...")

            # Go to home with human-like behavior
            self.page.goto('https://twitter.com/home', wait_until='networkidle')
            self._random_delay(5000, 8000)

            # Random mouse movement
            self._random_mouse_move()
            self._random_delay(3000, 5000)

            # Click tweet button
            try:
                print("📝 Opening tweet composer...")
                self._random_mouse_move()
                time.sleep(random.uniform(1.5, 3.5))

                self.page.click('a[data-testid="SideNav_NewTweet_Button"]')
                self._random_delay(3000, 5000)
            except:
                print("⚠️  Could not find tweet button")
                self.page.screenshot(path='error_twitter.png')
                return False

            # Type content with human-like delay
            print("📝 Typing tweet content...")
            self._random_mouse_move()
            time.sleep(random.uniform(1.0, 2.0))

            self.page.fill('div[data-testid="tweetTextarea_0"]', content)
            self._random_delay(8000, 15000)

            if dry_run:
                print("🧪 DRY RUN MODE - Not actually posting")
                print(f"📄 Would have posted: {content}")
                return True

            # Click Tweet button with human-like delay
            print("📤 Publishing tweet...")
            self._random_mouse_move()
            time.sleep(random.uniform(2.0, 4.0))

            self.page.click('button[data-testid="tweetButtonInline"]')
            self._random_delay(8000, 12000)

            print("✅ Successfully posted tweet!")
            return True

        except Exception as e:
            print(f"❌ Error posting: {e}")
            self.page.screenshot(path='error_twitter.png')
            return False
    
    def close(self):
        """Close browser (keeps session for next time)"""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        print("🔒 Browser closed (session preserved)")


def extract_content(filepath):
    """Extract content from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    post_lines = []
    in_content = False
    
    for line in lines:
        if '## Content' in line:
            in_content = True
            continue
        elif line.startswith('##') and in_content:
            break
        elif in_content and line.strip() and not line.strip().startswith('#'):
            post_lines.append(line.strip())
    
    # Twitter has 280 char limit
    full_content = '\n\n'.join(post_lines)
    if len(full_content) > 280:
        full_content = full_content[:277] + '...'
    
    return full_content


def post_to_twitter(filepath, headless=False, dry_run=False):
    """Main function to post to Twitter"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed")
        return False

    poster = None

    try:
        print("=" * 60)
        print("Twitter/X Poster (Playwright - Chrome Profile)")
        print("=" * 60)
        print()

        if dry_run:
            print("🧪 DRY RUN MODE - Will not actually post")
            print()

        # Extract content
        content = extract_content(filepath)
        print(f"📄 Content: {len(content)} characters")
        print()

        # Initialize poster
        poster = TwitterPosterPlaywright(headless=headless)
        poster.start()

        # Check login (no auto-login)
        if not poster.check_login():
            print()
            print("=" * 60)
            print("❌ FAILED - Not logged in")
            print("=" * 60)
            print()
            print("Please log in to Twitter/X manually in Chrome first:")
            print("1. Open Chrome browser")
            print("2. Go to https://twitter.com")
            print("3. Log in with your credentials")
            print("4. Close Chrome")
            print("5. Run this script again")
            return False

        # Post
        success = poster.post_tweet(content, dry_run=dry_run)

        if success:
            print()
            print("=" * 60)
            if dry_run:
                print("✅ DRY RUN SUCCESS! (Not actually posted)")
            else:
                print("✅ SUCCESS! Posted to Twitter/X")
            print("=" * 60)

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    finally:
        if poster:
            time.sleep(2)
            poster.close()


def main():
    import sys

    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv

    # Remove flags from argv
    args = [arg for arg in sys.argv[1:] if arg not in ['--dry-run', '-d']]

    if len(args) > 0:
        filepath = args[0]
    else:
        posted_folder = Path('03_Posted/History')
        posts = list(posted_folder.glob('*Twitter_Post_*.md'))

        if not posts:
            print("❌ No Twitter posts found")
            return

        filepath = max(posts, key=lambda p: p.stat().st_mtime)
        print(f"📄 Using: {filepath.name}\n")

    post_to_twitter(str(filepath), headless=False, dry_run=dry_run)


if __name__ == "__main__":
    main()
