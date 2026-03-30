#!/usr/bin/env python3
"""
X (Twitter) Autonomous Browser Agent
Author: Antigravity Digital FTE
Reliable browser automation for X (Twitter) posting.
"""

import os
import time
import datetime
import random
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Configuration
VAULT_PATH = Path(r"e:\Python.py\Hackaton 0\AI_Employee_Vault")
LOG_FILE = VAULT_PATH / "Logs" / "Twitter_Log.md"
WINDOW_SIZE = {'width': 1280, 'height': 800}
# Move session dir to avoid spaces in path which can cause launch instability
USER_DATA_DIR = Path("e:/Python.py/twitter_session") 

# Load Environment Variables
load_dotenv()
TWITTER_EMAIL = os.getenv('TWITTER_EMAIL')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')

class TwitterAutonomousAgent:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.context = None
        self.page = None

    def start_browser(self):
        """Step 1: Open browser with persistent profile & Set zoom"""
        print(f"🚀 Starting browser with profile: {USER_DATA_DIR}")
        
        # Ensure directory exists
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
            
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # Full cleanup of previous objects if retrying
                if self.context: 
                    try: self.context.close()
                    except: pass
                if self.playwright: 
                    try: self.playwright.stop()
                    except: pass
                
                self.playwright = sync_playwright().start()
                
                self.context = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=str(USER_DATA_DIR),
                    headless=self.headless,
                    viewport=WINDOW_SIZE,
                    user_agent=USER_AGENT,
                    ignore_https_errors=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )
                self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
                break
            except Exception as e:
                print(f"⚠️ Browser launch attempt {attempt + 1} failed: {e}")
                if "exitCode=21" in str(e) or attempt < max_retries - 1:
                    print("♻️ Recreating session directory...")
                    import shutil
                    try:
                        shutil.rmtree(USER_DATA_DIR, ignore_errors=True)
                        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
                    except: pass
                
                if attempt == max_retries - 1:
                    print("❌ Could not stabilize browser launch.")
                    return False

        # Advanced Stealth: Hide webdriver and spoof fingerprints
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(window, 'devicePixelRatio', { get: () => 1 });
            Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth });
            Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight });
        """)
        
        print("🔍 Resetting zoom (CTRL + 0)...")
        try:
            self.page.goto("https://x.com", wait_until="domcontentloaded", timeout=60000)
            self.page.keyboard.press("Control+0")
            time.sleep(1)
        except Exception:
            pass
        return True

    def is_logged_in(self):
        """Check if we are already logged in via saved session"""
        try:
            print("🔄 Checking if already logged in...")
            self.page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
            # Wait for home timeline
            self.page.wait_for_selector('div[data-testid="primaryColumn"]', timeout=30000)
            return "home" in self.page.url
        except:
            return False

    def click_safe(self, selectors, name="button"):
        """Wait for and click one of the selectors"""
        for selector in selectors:
            try:
                if self.page.is_visible(selector, timeout=5000):
                    print(f"    - Clicking {name} ({selector})...")
                    self.page.click(selector, timeout=10000)
                    return True
            except:
                continue
        return False

    def login(self):
        """Step 2: Login to X (Only if needed)"""
        if self.is_logged_in():
            print("✅ Session active! Bypassing login.")
            return True
            
        print(f"🔐 Attempting autonomous login for {TWITTER_EMAIL}...")
        
        for attempt in range(3):  # Up to 3 retries
            try:
                print(f"  - Login Attempt {attempt + 1}/3...")
                
                # 1. Open homepage first as requested
                print("  - Step 1: Opening homepage...")
                self.page.goto("https://x.com", wait_until="domcontentloaded", timeout=90000)
                self.page.wait_for_timeout(7000) # Wait for organic load
                
                # 2. Click the Sign in button
                print("  - Step 2: Clicking Sign in button...")
                login_selectors = [
                    'a[href="/login"]',
                    'div[role="button"]:has-text("Sign in")',
                    'span:has-text("Sign in")'
                ]
                
                clicked = False
                for sel in login_selectors:
                    if self.page.is_visible(sel, timeout=5000):
                        print(f"    - Found sign in button: {sel}")
                        self.page.click(sel)
                        clicked = True
                        break
                
                if not clicked:
                    print("    - Button not found, checking if already on login page...")
                sign_in_selectors = ['a[href="/login"]', 'div[role="button"]:has-text("Sign in")', 'a:has-text("Sign in")']
                
                # Ensure we are on login if homepage click fails or modal doesn't open
                self.click_safe(sign_in_selectors, "Sign in button")
                self.page.wait_for_timeout(3000)
                
                # RECOVERY SUB-LOOP (Internal retries for email/password flow)
                for sub_attempt in range(2):
                    print(f"  - Login Flow Attempt {sub_attempt + 1}...")
                    
                    # 3. Enter email
                    print("    - Entering email...")
                    email_selector = 'input[name="text"]'
                    try:
                        self.page.wait_for_selector(email_selector, timeout=20000)
                        self.page.click(email_selector)
                        self.page.wait_for_timeout(random.randint(500, 1500))
                        
                        # Ultra-stealth typing
                        for char in TWITTER_EMAIL:
                            self.page.keyboard.type(char)
                            time.sleep(random.uniform(0.1, 0.4))
                        
                        self.page.keyboard.press("Tab") # Blur to trigger validation
                        self.page.wait_for_timeout(2000)
                        
                        # Check if "Next" button is clickable
                        next_btn = self.page.locator('div[role="button"]:has-text("Next")')
                        if next_btn.count() > 0:
                            print("    - Clicking Next button...")
                            next_btn.click()
                        else:
                            print("    - Submitting via Enter...")
                            self.page.keyboard.press("Enter")
                            
                        self.page.wait_for_timeout(5000) # Give more time for transition
                    except Exception as e:
                        print(f"    - ⚠️ Email step failed: {e}. Reloading flow...")
                        self.page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")
                        self.page.wait_for_timeout(5000)
                        continue

                    # 4. Detect the next step (Flow A, B, or C)
                    print("    - Detecting next step...")
                    password_selectors = ["input[name='password']", "input[type='password']", 'input[data-testid="LoginForm_Password_Input"]']
                    username_verify_selector = 'input[data-testid="ocfEnterTextTextInput"]'
                    
                    target_found = None
                    for _ in range(15): # 15s timeout
                        if any(self.page.is_visible(s) for s in password_selectors):
                            target_found = "PASSWORD"
                            break
                        if self.page.is_visible(username_verify_selector):
                            target_found = "USERNAME"
                            break
                        if self.page.is_visible('text="Verify your identity"') or self.page.is_visible('text="security code"'):
                            target_found = "SECURITY"
                            break
                        
                        if not self.page.is_visible('div[role="dialog"]'):
                            print("      - ⚠️ Modal closed during detection.")
                            break
                        self.page.wait_for_timeout(1000)
                    
                    if not target_found:
                        print("    - 🔄 Recovery: Reloading flow for retry...")
                        self.page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")
                        self.page.wait_for_timeout(5000)
                        continue # Try the sub-loop again

                    if target_found == "USERNAME":
                        print("    - 👤 FLOW B: Username Confirmation")
                        username_val = TWITTER_USERNAME or TWITTER_EMAIL.split('@')[0]
                        self.page.fill(username_verify_selector, username_val)
                        self.page.keyboard.press("Enter")
                        self.page.wait_for_timeout(3000)
                    elif target_found == "SECURITY":
                        print("    - 🛡️ FLOW C: Security Check")
                        self.page.screenshot(path="login_security_check.png")
                        raise Exception("Security Verification required.")

                    # 5. Enter password
                    print("    - Entering password...")
                    active_pw_sel = None
                    for _ in range(10): 
                        for s in password_selectors:
                            if self.page.is_visible(s):
                                active_pw_sel = s
                                break
                        if active_pw_sel: break
                        self.page.wait_for_timeout(1000)
                    
                    if not active_pw_sel:
                        print("    - ⚠️ Password field missed. Retrying sub-flow...")
                        continue
                    
                    self.page.fill(active_pw_sel, TWITTER_PASSWORD)
                    self.page.keyboard.press("Enter")
                    
                    # 6. Verify Timeline
                    print("    - Verifying timeline...")
                    try:
                        self.page.wait_for_selector('div[data-testid="primaryColumn"]', timeout=30000)
                        print("✅ Login successful!")
                        return True
                    except:
                        print("    - ⚠️ Timeline not reached.")
                
                raise Exception("Exhausted sub-attempts for this login attempt.")
                
            except Exception as e:
                print(f"❌ Login Attempt {attempt+1} failed: {e}")
                self.page.screenshot(path=f"login_fail_attempt_{attempt+1}.png")
                time.sleep(5)
        return False

    def generate_tweet(self):
        """Step 3: Generate AI Content"""
        tweets = [
            "AI Employees are changing the future of work. A Digital FTE can work 24/7, automate tasks, and scale businesses faster. The future is Human + AI collaboration. #AI #Automation #FutureOfWork",
            "The era of AI automation is here. Digital employees aren't just tools; they are teammates that handle routine tasks so humans can focus on creativity. #AI #Innovation #DigitalFTE",
            "Scaling a business is easier with AI automation. Imagine a workforce that never sleeps and always executes with precision. That's the power of Digital FTEs. #Automation #BusinessGrowth #AI"
        ]
        return random.choice(tweets)

    def create_post(self, content):
        """Step 4 & 5: Create and Publish Post"""
        print(f"📝 Posting tweet: {content[:50]}...")
        
        post_selectors = [
            'div[data-testid="SideNav_NewTweet_Button"]',
            'a[data-testid="SideNav_NewTweet_Button"]',
            'div[aria-label="Post"]',
            'a[aria-label="Post"]'
        ]
        
        for i in range(3):
            print(f"  - Post attempt {i+1}/3...")
            try:
                if "home" not in self.page.url:
                    self.page.goto("https://x.com/home", wait_until="domcontentloaded")
                    self.page.wait_for_selector('div[data-testid="primaryColumn"]', timeout=20000)

                clicked = False
                for selector in post_selectors:
                    if self.page.is_visible(selector):
                        self.page.click(selector)
                        clicked = True
                        break
                
                if not clicked:
                    self.page.keyboard.press("n")
                
                self.page.wait_for_timeout(3000)
                self.page.wait_for_selector('div[data-testid="tweetTextarea_0"]', timeout=15000)
                self.page.fill('div[data-testid="tweetTextarea_0"]', content)
                self.page.wait_for_timeout(2000)
                
                publish_selector = 'div[data-testid="tweetButtonInline"]'
                if not self.page.is_visible(publish_selector):
                    publish_selector = 'button[data-testid="tweetButton"]'
                
                self.page.click(publish_selector)
                
                # Check for success on timeline
                time.sleep(5)
                print("✅ Tweet published successfully!")
                return True
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

    def logout_and_close(self):
        """Step 10: Logout & Cleanup"""
        print("🔒 Logging out safely...")
        try:
            if not self.page: return
            
            # Click Account Switcher
            switcher = self.page.locator('div[data-testid="SideNav_AccountSwitcher_Button"]')
            if switcher.count() > 0:
                switcher.click()
                self.page.wait_for_timeout(2000)
                
                # Click Logout option
                logout_btns = [
                    'a[data-testid="AccountSwitcher_Logout_Button"]',
                    'a:has-text("Log out")',
                    '//span[text()="Log out"]/ancestor::a'
                ]
                
                for sel in logout_btns:
                    btn = self.page.locator(sel)
                    if btn.count() > 0:
                        btn.click()
                        confirm = self.page.locator('button[data-testid="confirmationSheetConfirm"]')
                        if confirm.count() > 0:
                            confirm.click()
                            print("✅ Logged out.")
                        break
        except Exception as e:
            print(f"⚠️ Logout skipped: {e}")
        
        try:
            if self.context: self.context.close()
            if self.playwright: self.playwright.stop()
            print("👋 Session closed.")
        except: pass

def main():
    agent = TwitterAutonomousAgent(headless=False)
    try:
        if not (TWITTER_EMAIL and TWITTER_PASSWORD):
            print("❌ Error: TWITTER_EMAIL and TWITTER_PASSWORD must be in .env")
            return
        if not agent.start_browser():
            return

        if not agent.is_logged_in():
            if not agent.login():
                print("❌ Final diagnosis: Login failed after all retries.")
                return

        tweet_text = agent.generate_tweet()
        if agent.post_tweet(tweet_text):
            agent.log_to_vault(f"Tweet Posted: {tweet_text}")
            print("🚀 Task Completed Successfully")
        else:
            print("❌ Failed to post tweet.")
    except Exception as e:
        print(f"💥 Fatal script error: {e}")
    finally:
        agent.logout_and_close()

if __name__ == "__main__":
    main()
