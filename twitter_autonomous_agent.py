#!/usr/bin/env python3
"""
X (Twitter) Autonomous Browser Agent - Chrome Profile Edition
Author: Antigravity Digital FTE
Reliable browser automation for X (Twitter) posting using real Chrome profile.
NO AUTO-LOGIN - Uses existing Chrome session.
"""

import os
import sys
import time
import random
import urllib.parse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Add vault to path for imports
sys.path.insert(0, str(Path(__file__).parent / "AI_Employee_Vault" / "twitter"))
from session_manager import TwitterSessionManager

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
LOG_FILE = VAULT_PATH / "Logs" / "Twitter_Log.md"
WINDOW_SIZE = {'width': 1366, 'height': 768}

# Load Environment Variables
load_dotenv()
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = os.getenv("CHROME_PROFILE", "Default")
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME', '')

class TwitterAutonomousAgent:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.context = None
        self.page = None
        self.session_manager = TwitterSessionManager()
        self.user_data_dir = os.path.join(CHROME_USER_DATA, CHROME_PROFILE)

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

    def start_browser(self):
        """Step 1: Open browser with real Chrome profile"""
        print(f"🚀 Starting browser with Chrome profile: {self.user_data_dir}")

        try:
            self.playwright = sync_playwright().start()

            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel="chrome",
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--start-maximized',
                    '--ignore-certificate-errors',
                    '--password-store=basic'
                ],
                no_viewport=True
            )

            # Advanced Stealth
            self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            """)

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

            print("✅ Browser started successfully")
            return True

        except Exception as e:
            print(f"❌ Browser launch failed: {e}")
            return False

    def is_logged_in(self):
        """Check if already logged in using session manager"""
        try:
            print("🔄 Checking login status...")
            return self.session_manager.check_login_status(self.page)
        except Exception as e:
            print(f"❌ Login check failed: {e}")
            return False

    def check_login(self):
        """Step 2: Check if logged in (NO AUTO-LOGIN)"""
        if self.is_logged_in():
            print("✅ Already logged in!")
            return True
        else:
            print("❌ Not logged in to Twitter/X")
            print("⚠️  Please log in manually in Chrome first:")
            print("   1. Open Chrome browser")
            print("   2. Go to https://twitter.com")
            print("   3. Log in with your credentials")
            print("   4. Close Chrome")
            print("   5. Run this script again")
            return False

    def generate_tweet(self):
        """Step 3: Generate AI Content"""
        tweets = [
            "AI Employees are changing the future of work. A Digital FTE can work 24/7, automate tasks, and scale businesses faster. The future is Human + AI collaboration. #AI #Automation #FutureOfWork",
            "The era of AI automation is here. Digital employees aren't just tools; they are teammates that handle routine tasks so humans can focus on creativity. #AI #Innovation #DigitalFTE",
            "Scaling a business is easier with AI automation. Imagine a workforce that never sleeps and always executes with precision. That's the power of Digital FTEs. #Automation #BusinessGrowth #AI"
        ]
        tweet = random.choice(tweets)
        # Add Timestamp to start for absolute uniqueness
        timestamp_str = datetime.now().strftime("%H:%M:%S")
        tweet = f"[{timestamp_str}] {tweet}"
        
        # Append unique ID as well for double safety
        unique_id = f" [ID:{random.randint(1000, 9999)}]"
        limit = 250 - len(unique_id)
        if len(tweet) > limit:
            tweet = tweet[:limit-3] + "..."
        return tweet + unique_id

    def create_post(self, content, dry_run=False):
        """Step 4 & 5: Create and Publish Post with anti-detection"""
        print(f"📝 Posting tweet: {content[:50]}...")

        for i in range(3):
            print(f"  - Post attempt {i+1}/3...")
            try:
                # Anti-detection: random delays and mouse movements
                self._random_mouse_move()
                self._random_delay(8000, 15000)

                # Ensure we're on home
                if "home" not in self.page.url.lower():
                    print("      - Navigating to home page...")
                    self.page.goto("https://twitter.com/home", wait_until="load", timeout=60000)
                
                time.sleep(3)
                
                # --- Overlay Handling ---
                try:
                    self.page.evaluate("() => { document.querySelectorAll('[data-testid=\"twc-cc-mask\"], .css-175oi2r.r-1pi2tsx').forEach(m => m.style.display = 'none'); }")
                except: pass

                # Open Modal
                try:
                    sidebar_btn = self.page.locator('[data-testid="SideNav_NewTweet_Button"]:visible').first
                    sidebar_btn.click()
                    print("      - Sidebar Post button clicked.")
                except:
                    print("      ⚠️ Sidebar button not found, using keyboard 'n'...")
                    self.page.keyboard.press("n")

                time.sleep(2)

                # TARGET TEXTAREA
                print("      - Filling tweet content in modal...")
                tweet_input = self.page.locator('div[data-testid="tweetTextarea_0"]:visible, div[role="textbox"]:visible').first
                tweet_input.wait_for(state="visible", timeout=30000)
                
                # --- FORCE FOCUS ---
                tweet_input.scroll_into_view_if_needed()
                tweet_input.click()
                time.sleep(0.5)
                tweet_input.fill("")
                time.sleep(0.5)
                
                # Human-like interaction
                for char in content:
                    self.page.keyboard.type(char, delay=random.randint(10, 30))
                
                time.sleep(0.8)
                self.page.keyboard.press("Space")
                self.page.keyboard.press("Backspace")
                time.sleep(1)

                if dry_run:
                    print("🧪 DRY RUN - Not actually posting")
                    return True

                # Wait for button
                publish_selector = '[data-testid="tweetButton"]:visible:not([aria-disabled="true"])'
                
                posted = False
                try:
                    self.page.wait_for_selector(publish_selector, timeout=30000)
                    print("✅ Post button is now enabled!")
                    
                    # Click Post
                    button = self.page.locator('[data-testid="tweetButton"]:visible').first
                    box = button.bounding_box()
                    if box:
                        self.page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                    else:
                        button.click()
                        
                    # Verify closure
                    self.page.wait_for_selector('div[data-testid="tweetTextarea_0"]', state="detached", timeout=12000)
                    print("✅ Tweet posted successfully!")
                    posted = True
                except:
                    print("⚠️ Modal still open, re-focusing and trying Keyboard Fallback...")
                    
                    # --- CRITICAL RE-FOCUS ---
                    try:
                        box = tweet_input.bounding_box()
                        if box:
                            self.page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/4)
                    except:
                        tweet_input.focus()
                    
                    time.sleep(0.5)
                    self.page.keyboard.press("Control+Enter")
                    try:
                        self.page.wait_for_selector('div[data-testid="tweetTextarea_0"]', state="detached", timeout=12000)
                        print("✅ Tweet posted via keyboard fallback!")
                        posted = True
                    except:
                        print("❌ Still failed — possibly blocked or focus issues")
                        posted = False

                # 🔥 FINAL STATUS OUTPUT
                print("\n" + "="*70)
                if posted:
                    print("✅ FULLY POSTED")
                    print("="*70)
                    return True
                else:
                    print("❌ POSTING FAILED")
                    print("="*70)
                    continue
            except Exception as e:
                print(f"    ❌ Attempt {i+1} failed: {str(e)}")
                time.sleep(5)
        return False

    def capture_url(self):
        """Step 6: Capture Tweet URL"""
        print("🔗 Capturing tweet URL...")
        try:
            username = TWITTER_USERNAME or TWITTER_EMAIL.split('@')[0].replace('.', '')
            self.page.goto(f"https://x.com/{username}", wait_until="domcontentloaded", timeout=60000)
            self.page.wait_for_selector('article[data-testid="tweet"]', timeout=20000)
            href = self.page.eval_on_selector('article[data-testid="tweet"] a[href*="/status/"]', 'el => el.href')
            print(f"✅ URL Captured: {href}")
            return href
        except Exception as e:
            print(f"⚠️ Could not capture URL: {str(e)}")
            return "Unknown"

    def save_log(self, content, url):
        """Step 7: Save to Log File"""
        print(f"💾 Saving log to {LOG_FILE}...")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n---\n**Date:** {date_str}\n**Tweet Content:** {content}\n**Tweet URL:** {url}\n**Status:** Posted\n"
        
        try:
            if not LOG_FILE.parent.exists():
                LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print("✅ Activity logged successfully.")
        except Exception as e:
            print(f"❌ Logging failed: {str(e)}")

    def close_browser(self):
        """Step 10: Close browser (keep session for next time)"""
        print("🔒 Closing browser (session preserved)...")
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            print("👋 Browser closed.")
        except Exception as e:
            print(f"⚠️ Close error: {e}")

def main():
    """Main execution function"""
    agent = TwitterAutonomousAgent(headless=False)
    try:
        print("=" * 60)
        print("Twitter Autonomous Agent - Chrome Profile Edition")
        print("=" * 60)
        print()

        # Start browser
        if not agent.start_browser():
            print("❌ Failed to start browser")
            return

        # Check login (no auto-login)
        if not agent.check_login():
            print("❌ Not logged in - please log in manually first")
            return

        # Generate tweet
        tweet_text = agent.generate_tweet()
        print(f"\n📝 Generated tweet: {tweet_text}\n")

        # Post tweet
        if agent.create_post(tweet_text):
            # Capture URL
            tweet_url = agent.capture_url()

            # Save log
            agent.save_log(tweet_text, tweet_url)

            print("\n" + "=" * 60)
            print("🚀 Task Completed Successfully")
            print("=" * 60)
        else:
            print("❌ Failed to post tweet")

    except Exception as e:
        print(f"💥 Fatal error: {e}")
    finally:
        agent.close_browser()

if __name__ == "__main__":
    main()
