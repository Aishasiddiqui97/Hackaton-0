#!/usr/bin/env python3
"""
Facebook Poster using Playwright
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

load_dotenv()

FACEBOOK_EMAIL = os.getenv('FACEBOOK_EMAIL', '')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD', '')


class FacebookPosterPlaywright:
    """Facebook automation using Playwright"""
    
    def __init__(self, headless=True):
        self.email = FACEBOOK_EMAIL
        self.password = FACEBOOK_PASSWORD
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        
    def start(self):
        """Start browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']
        )
        
        # Load existing session if available
        if os.path.exists('facebook_auth.json'):
            print("💾 Loading saved Facebook session...")
            context = self.browser.new_context(
                viewport={'width': 1280, 'height': 900},
                device_scale_factor=1,
                storage_state='facebook_auth.json'
            )
        else:
            context = self.browser.new_context(
                viewport={'width': 1280, 'height': 900},
                device_scale_factor=1
            )
            
        self.page = context.new_page()
        self.context = context
        print("✅ Browser started")
        
    def login(self):
        """Login to Facebook"""
        try:
            print("🔐 Checking Facebook login...")
            self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded')
            time.sleep(4)
            
            # CORRECT CHECK: Facebook shows login form on facebook.com/ WITHOUT changing the URL
            # So we must check if the login form (email input) is VISIBLE, not the URL
            login_form_visible = False
            try:
                login_form_visible = self.page.is_visible('input[name="email"]', timeout=3000)
            except:
                pass
            
            if not login_form_visible:
                print("✅ Already logged in from session!")
                return True
            
            # Session expired or no session - do fresh login
            print("🔐 Session expired or missing. Logging in with credentials...")
            time.sleep(1)
            
            # Enter email
            self.page.fill('input[name="email"]', self.email)
            
            # Enter password
            self.page.fill('input[name="pass"]', self.password)
            
            # Press Enter to login (more reliable than clicking the button)
            self.page.keyboard.press("Enter")
            
            # Optional fallback: click if the button is visible, but don't time out if it's not
            try:
                if self.page.is_visible('button[name="login"]', timeout=2000):
                    self.page.click('button[name="login"]')
            except:
                pass
            
            time.sleep(4)
            
            # Wait up to 120 seconds for Facebook to process the login or for human to solve captcha/2FA
            print("⏳ Waiting up to 120 seconds. IF YOU SEE A CAPTCHA or 2FA/CODELOGIN, PLEASE SOLVE IT MANUALLY NOW in the browser window!")
            
            # Positive indicators that we are actually on the home page
            home_indicators = [
                'div[role="main"]',
                'div[aria-label="Facebook"][role="banner"]',
                'a[aria-label="Facebook"]',
                'div[data-pagelet="Stories"]',
                'div[role="feed"]'
            ]
            
            # Negative indicators (still on login/2FA)
            pending_indicators = [
                ('input[name="approvals_code"]', "Two-Factor Authentication Code"),
                ('input[id="approvals_code"]', "Two-Factor Authentication Code"),
                ('div[id="login_error"]', "Login Error Message"),
                ('#checkpointSubmitButton', "Security Checkpoint"),
                ('button[name="reset_action"]', "Password Reset/Checkpoint")
            ]

            success = False
            for i in range(24): # 24 * 5 = 120 seconds
                current_url = self.page.url
                
                # Check for home page indicators
                for ind in home_indicators:
                    try:
                        if self.page.is_visible(ind, timeout=1000):
                            print(f"✅ Home page detected via: {ind}")
                            success = True
                            break
                    except:
                        pass
                
                if success:
                    break
                    
                # Check for 2FA/Login issues
                for selector, label in pending_indicators:
                    try:
                        if self.page.is_visible(selector, timeout=500):
                            print(f"⏳ Still on {label} screen. Please solve it now!")
                            break
                    except:
                        pass

                if i % 4 == 0 and i > 0:
                    print(f"   Still waiting... ({i*5}s elapsed, Current URL: {current_url[:100]}...)")
                time.sleep(5)
            
            final_url = self.page.url
            if success:
                print("✅ Login successful!")
                self.context.storage_state(path='facebook_auth.json')
                print("💾 Session saved to facebook_auth.json (Next time login won't be required)")
                return True
            else:
                print(f"⚠️  Login failed or timed out. Current URL: {final_url}")
                self.page.screenshot(path='login_error_fb.png')
                print("📸 Screenshot saved as 'login_error_fb.png'.")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def post_content(self, content):
        """Post to Facebook"""
        try:
            print("📝 Ensuring we are on Facebook home...")
            
            # After login, browser may already be on facebook.com
            # Wait for page to stabilize instead of doing a new goto()
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=10000)
            except:
                pass
            time.sleep(3)

            # Only navigate if not already on the home feed
            current_url = self.page.url
            print(f"   Current URL: {current_url}")
            if 'facebook.com' not in current_url or 'login' in current_url or 'two_step' in current_url:
                try:
                    self.page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=15000)
                    time.sleep(5)
                except Exception as nav_err:
                    print(f"⚠️  Navigation warning: {nav_err}")
                    time.sleep(3)

            # Wait for any "feed" element to appear to confirm we are actually logged in and on home
            feed_selectors = ['div[role="main"]', 'div[aria-label="Stories"]', 'div[data-pagelet="Stories"]', 'div[aria-label="Facebook"]']
            feed_found = False
            for sel in feed_selectors:
                if self.page.is_visible(sel):
                    feed_found = True
                    break
            
            if not feed_found:
                print("⏳ Feed not visible yet, waiting and scrolling...")
                self.page.mouse.wheel(0, 300)
                time.sleep(4)


            # Take screenshot to see current state
            self.page.screenshot(path='debug_fb_home.png')
            print("📸 Home page screenshot saved as debug_fb_home.png")

            print("🔍 Looking for post compose box...")

            # Try to find compose box with multiple retries and scrolling
            compose_found = False
            for attempt in range(3):
                xpath_selectors = [
                    "//div[@role='button']//span[contains(text(), \"What's on your mind\")]",
                    "//div[@role='button']//span[contains(text(), \"Aap ke zehen mein kya hai\")]",
                    "//div[@role='button']//span[contains(text(), \"ذہن\")]",
                    "//div[contains(@aria-label, \"What's on your mind\")]",
                    "//div[contains(@aria-label, \"Create a post\")]",
                    "//div[contains(@aria-label, \"Post\")]",
                    "//div[contains(@aria-label, \"ذہن\")]",
                    "//div[@role='main']//div[@role='button'][contains(., \"What's on\")]",
                    "//div[@role='main']//div[@role='button'][contains(., \"ذہن\")]",
                    "//div[@data-testid='status-attachment-mentions-input']",
                    # Very generic: find any button in the main area that looks like a composer
                    "//div[@role='main']//div[@role='button']//div[contains(text(), 'What')]",
                    "//div[@role='main']//div[@role='button']//div[contains(text(), 'ذہن')]",
                ]

                for xpath in xpath_selectors:
                    try:
                        el = self.page.locator(f"xpath={xpath}").first
                        if el.is_visible(timeout=2000):
                            # Try click, then force click, then Enter
                            el.click(timeout=2000)
                            time.sleep(1)
                            compose_found = True
                            print(f"✅ Compose box clicked via: {xpath}")
                            break
                    except:
                        try:
                            el.click(force=True)
                            time.sleep(1)
                            compose_found = True
                            print(f"✅ Compose box click FORCED via: {xpath}")
                            break
                        except:
                            continue
                
                if compose_found:
                    break
                
                print(f"   Attempt {attempt+1} failed, scrolling...")
                self.page.mouse.wheel(0, 400)
                time.sleep(2)

            if not compose_found:
                # Last resort: navigate directly to /composer
                print("⚠️ Compose box not found. Trying direct composer URL...")
                self.page.goto('https://www.facebook.com/?composer=true', wait_until='domcontentloaded')
                time.sleep(4)
                self.page.screenshot(path='debug_fb_composer.png')

            # Step 2: Patience for dialog
            print("⏳ Waiting for text area to appear...")
            time.sleep(3)

            # Step 3: Find the contenteditable text area using multiple approaches
            typed = False
            text_xpaths = [
                "//div[@role='dialog']//div[@contenteditable='true']",
                "//div[@role='presentation']//div[@contenteditable='true']",
                "//div[@contenteditable='true'][@role='textbox']",
                "//div[contains(@aria-label, 'mind')]//div[@contenteditable='true']",
                "//div[contains(@aria-label, 'ذہن')]//div[@contenteditable='true']",
                "//div[@aria-autocomplete='list']",
                "//div[@aria-multiline='true']",
                "//div[@contenteditable='true']",
                "//div[@role='textbox']",
                "//div[@name='xhpc_message']",
            ]

            # Try to click and type with more patience
            for xpath in text_xpaths:
                try:
                    el = self.page.locator(f"xpath={xpath}").first
                    # Look for it multiple times within a short period
                    for _ in range(4):
                        if el.is_visible(timeout=1000):
                            el.click(force=True)
                            time.sleep(1)
                            # Clear if necessary
                            self.page.keyboard.press("Control+a")
                            self.page.keyboard.press("Backspace")
                            time.sleep(0.5)
                            self.page.keyboard.type(content, delay=35)
                            typed = True
                            print(f"✅ Typed content into: {xpath}")
                            break
                        
                        # If still not typed, try closing a potential "Turn on Notifications" pop-up
                        if _ == 2: # On 3rd attempt, specifically try to bypass overlays
                            try:
                                # Look for "Not Now" buttons specifically (English and Urdu)
                                not_now = self.page.locator("//div[@role='button'][contains(., 'Not Now') or contains(., 'ابھی نہیں')]").first
                                if not_now.is_visible(timeout=1000):
                                    not_now.click()
                                    print("   Closed 'Not Now' overlay")
                                    time.sleep(1)
                            except:
                                pass
                        
                        time.sleep(1)
                    if typed:
                        break
                except:
                    continue

            if not typed:
                self.page.screenshot(path='error_fb_textarea.png')
                print("❌ Could not find text area. Screenshot saved.")
                return False

            time.sleep(2)

            # Step 4: Click Post button with robustness
            print("📤 Looking for Post button...")
            time.sleep(4) # Wait for content to sync and button to enable
            
            # Post button often has specific aria-label or text
            post_xpaths = [
                "//div[@aria-label='Post'][@role='button']",
                "//div[@aria-label='پوسٹ کریں'][@role='button']",
                "//div[@role='dialog']//div[@role='button']//span[text()='Post']",
                "//div[@role='dialog']//div[@role='button']//span[text()='پوسٹ کریں']",
                "//div[@role='dialog']//div[@role='button'][@aria-disabled='false'][contains(., 'Post')]",
                "//div[@role='dialog']//div[@role='button'][@aria-disabled='false'][contains(., 'پوسٹ')]",
            ]
            
            posted = False
            for xpath in post_xpaths:
                try:
                    el = self.page.locator(f"xpath={xpath}").first
                    if el.is_visible(timeout=3000):
                        # Ensure it's not disabled
                        is_disabled = el.get_attribute("aria-disabled")
                        if is_disabled == "true":
                            print(f"   Button found but DISABLED ({xpath}). Waiting...")
                            time.sleep(3)
                        
                        el.scroll_into_view_if_needed()
                        el.click(force=True)
                        posted = True
                        print(f"✅ Clicked Post button via: {xpath}")
                        break
                except:
                    continue

            if not posted:
                print("⌨️ Post button not found with primary selectors. Trying generic search and Enter...")
                self.page.keyboard.press('Control+Enter')
                time.sleep(2)
                posted = True

            # Step 4b: Verify dialog CLOSES (this confirms the post was sent)
            dialog_selector = "//div[@role='dialog']"
            try:
                # Wait for dialog to disappear
                self.page.wait_for_selector(dialog_selector, state='hidden', timeout=10000)
                print("✅ Composer dialog disappeared (Post likely sent!)")
            except:
                print("⚠️ Dialog still visible after clicking Post. Trying Enter fallback...")
                self.page.keyboard.press('Enter')
                time.sleep(3)

            print("⏳ Waiting for post to upload and stabilize (20s)...")
            time.sleep(20)
            
            # Step 5: Verification
            print("📸 Taking post verification screenshot...")
            # Step 5: Verification with more resilience
            print("📸 Taking post verification screenshot...")
            try:
                # Use a slightly more robust navigation
                self.page.goto('https://www.facebook.com/me', wait_until='domcontentloaded', timeout=45000)
                time.sleep(5)
                self.page.reload(wait_until='domcontentloaded')
                time.sleep(8)
                self.page.mouse.wheel(0, 600)
                time.sleep(3)
                self.page.screenshot(path='post_validation.png')
                print("✅ Post validation screenshot saved as post_validation.png")
            except Exception as v_err:
                print(f"⚠️  Verification navigation issue: {v_err}")
                # Take whatever we have
                self.page.screenshot(path='post_validation_partial.png')

            print("✅ Successfully posted to Facebook!")
            return True

        except Exception as e:
            print(f"❌ Error posting: {e}")
            try:
                self.page.screenshot(path='error_facebook.png')
            except:
                pass
            return False

    
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("🔒 Browser closed")


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
    
    return '\n\n'.join(post_lines)


def post_to_facebook(filepath, headless=True):
    """Main function to post to Facebook"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed")
        return False
    
    if not FACEBOOK_EMAIL or not FACEBOOK_PASSWORD:
        print("❌ Facebook credentials not found in .env")
        return False
    
    poster = None
    
    try:
        print("=" * 60)
        print("Facebook Poster (Playwright)")
        print("=" * 60)
        print()
        
        # Extract content
        content = extract_content(filepath)
        
        # Add a unique identifier/timestamp to avoid duplication filter
        # Facebook often hides identical posts from the same source
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"{content}\n\n[Auto-Post Ref: {now}]"
        
        print(f"📄 Content: {len(content)} characters (Unique ref added)")
        print()
        
        # Initialize poster
        poster = FacebookPosterPlaywright(headless=headless)
        poster.start()
        
        # Login
        if not poster.login():
            return False
        
        # Post
        success = poster.post_content(content)
        
        if success:
            print()
            print("=" * 60)
            print("✅ SUCCESS! Posted to Facebook")
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
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        posted_folder = Path('03_Posted/History')
        posts = list(posted_folder.glob('*Facebook_Post_*.md'))
        
        if not posts:
            print("❌ No Facebook posts found")
            return
        
        filepath = max(posts, key=lambda p: p.stat().st_mtime)
        print(f"📄 Using: {filepath.name}\n")
    
    post_to_facebook(str(filepath), headless=False)


if __name__ == "__main__":
    main()
