#!/usr/bin/env python3
"""
Twitter/X Browser Automation MCP Server - Gold Tier
Autonomous browser-based Twitter posting with retry logic
Uses real Chrome profile - NO AUTO-LOGIN
"""

import json
import logging
import sys
import os
import time
import random
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

# Add vault to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "AI_Employee_Vault" / "twitter"))
from session_manager import TwitterSessionManager

# Logging setup
LOG_PATH = Path("logs/twitter_browser_actions.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [TWITTER_BROWSER] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Vault paths
VAULT_PATH = Path("AI_Employee_Vault")
LOGS_PATH = VAULT_PATH / "Logs"
PLANS_PATH = VAULT_PATH / "Plans"

# Chrome profile
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = os.getenv("CHROME_PROFILE", "Default")


class TwitterBrowserAgent:
    """Browser automation agent for Twitter/X posting using real Chrome profile."""

    def __init__(self):
        self.context = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.tweet_url = None
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

    def start_browser(self) -> bool:
        """Initialize browser session with real Chrome profile."""
        try:
            logger.info("TWITTER_BROWSER_START - Initializing Playwright with Chrome profile")

            self.playwright = sync_playwright().start()

            profile_path = os.path.join(CHROME_USER_DATA, CHROME_PROFILE)
            logger.info(f"TWITTER_BROWSER - Using profile: {profile_path}")

            # Launch persistent context with real Chrome profile
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=profile_path,
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

            logger.info("TWITTER_BROWSER_SUCCESS - Browser initialized")
            return True

        except Exception as e:
            logger.error(f"TWITTER_BROWSER_ERROR - Failed to start browser: {str(e)}")
            return False

    def check_login(self) -> bool:
        """Check if already logged in using session manager."""
        try:
            logger.info("TWITTER_LOGIN_CHECK - Verifying login status")

            # Use session manager to check login
            is_logged_in = self.session_manager.check_login_status(self.page)

            if is_logged_in:
                logger.info("TWITTER_LOGIN_SUCCESS - Already logged in")
                return True
            else:
                logger.error("TWITTER_LOGIN_FAILED - Not logged in")
                return False

        except Exception as e:
            logger.error(f"TWITTER_LOGIN_ERROR - {str(e)}")
            return False

    def generate_tweet(self) -> str:
        """Generate AI-focused tweet content."""
        tweets = [
            "AI employees are not replacing humans — they're giving businesses superpowers. A Digital FTE can work 24/7, handle operations, and scale instantly. The future of work is human + AI collaboration. #AI #Automation #DigitalEmployee",

            "Building autonomous AI agents that actually work is harder than it looks. But when done right, they transform how businesses operate. Here's what I learned building a Digital FTE system. #AIAutomation #FutureOfWork",

            "The best AI employees don't try to replace humans. They handle the repetitive tasks so humans can focus on strategy, creativity, and growth. That's the real productivity unlock. #AI #Productivity #BusinessAutomation",

            "Imagine an employee that never sleeps, never makes mistakes, and scales infinitely. That's what AI automation brings to modern businesses. The question isn't if you'll adopt it, but when. #AIEmployee #DigitalTransformation",

            "We built a Digital FTE that monitors emails, posts on social media, manages accounting, and generates executive reports. All autonomous. All logged. All with human oversight. This is the future. #AI #Automation #GoldTier"
        ]

        tweet = random.choice(tweets)

        # Ensure under 275 characters (keeping safe margin for spaces/emojis)
        if len(tweet) > 275:
            tweet = tweet[:272] + "..."

        logger.info(f"TWITTER_GENERATE - Tweet: {tweet[:50]}...")
        return tweet

    def post_tweet(self, content: str, max_retries: int = 3, dry_run: bool = False) -> bool:
        """Post tweet with retry logic and anti-detection measures."""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"TWITTER_POST_ATTEMPT - Attempt {attempt}/{max_retries}")
                # Step 4: Use Home-page Modal for posting
                logger.info("TWITTER_POST - Ensuring we're on home page")
                if "home" not in self.page.url.lower():
                    self.page.goto("https://twitter.com/home", wait_until="load", timeout=60000)
                
                time.sleep(3)
                
                # --- Overlay Handling ---
                try:
                    self.page.evaluate("() => { document.querySelectorAll('[data-testid=\"twc-cc-mask\"], .css-175oi2r.r-1pi2tsx').forEach(m => m.style.display = 'none'); }")
                except: pass

                # Open Modal
                logger.info("TWITTER_POST - Opening modal composer")
                try:
                    sidebar_btn = self.page.locator('[data-testid="SideNav_NewTweet_Button"]:visible').first
                    sidebar_btn.click()
                except:
                    self.page.keyboard.press("n")

                time.sleep(2)

                # TARGET TEXTAREA
                logger.info("TWITTER_POST - Filling tweet content in modal")
                tweet_input = self.page.locator('div[data-testid="tweetTextarea_0"]:visible, div[role="textbox"]:visible').first
                tweet_input.wait_for(state="visible", timeout=30000)
                
                # --- FORCE FOCUS ---
                tweet_input.scroll_into_view_if_needed()
                tweet_input.click()
                time.sleep(0.5)
                tweet_input.fill("")
                time.sleep(0.5)
                
                # Human-like interaction
                timestamp_str = datetime.now().strftime("%H:%M:%S")
                full_content = f"[{timestamp_str}] {content}"
                
                for char in full_content:
                    self.page.keyboard.type(char, delay=random.randint(10, 30))
                
                time.sleep(0.8)
                self.page.keyboard.press("Space")
                self.page.keyboard.press("Backspace")
                time.sleep(1)

                if dry_run:
                    logger.info("TWITTER_POST - DRY RUN MODE - Not actually posting")
                    self.tweet_url = "DRY_RUN_MODE"
                    return True

                # Wait for button
                publish_selector = '[data-testid="tweetButton"]:visible:not([aria-disabled="true"])'
                
                posted = False
                try:
                    self.page.wait_for_selector(publish_selector, timeout=30000)
                    logger.info("TWITTER_POST - Post button is now enabled!")
                    
                    # Click Post
                    button = self.page.locator('[data-testid="tweetButton"]:visible').first
                    box = button.bounding_box()
                    if box:
                        self.page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                    else:
                        button.click()
                        
                    # Verify closure
                    self.page.wait_for_selector('div[data-testid="tweetTextarea_0"]', state="detached", timeout=12000)
                    logger.info("TWITTER_POST_SUCCESS - Tweet posted and modal closed")
                    posted = True
                except:
                    logger.warning("TWITTER_POST - Modal still visible, re-focusing and trying keyboard fallback (Control+Enter)")
                    
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
                        logger.info("TWITTER_POST_SUCCESS - Tweet posted via keyboard fallback")
                        posted = True
                    except:
                        logger.error("TWITTER_POST_FAILED - Still visible even after keyboard fallback")
                        posted = False

                # 🔥 FINAL STATUS OUTPUT
                print("\n" + "="*70)
                if posted:
                    print("✅ FULLY POSTED")
                else:
                    print("❌ POSTING FAILED")
                print("="*70)

                if not posted:
                    continue

                # Wait for tweet to be posted
                self._random_delay(8000, 12000)

                # Capture tweet URL from timeline
                logger.info("TWITTER_POST - Capturing tweet URL")

                # Navigate to profile to find latest tweet
                profile_link = self.page.locator('[data-testid="AppTabBar_Profile_Link"]').first

                # Random mouse movement
                self._random_mouse_move()
                time.sleep(random.uniform(1.5, 3.0))

                profile_link.click()
                self._random_delay(5000, 8000)

                # Get first tweet link
                tweet_links = self.page.locator('article a[href*="/status/"]').all()
                if tweet_links:
                    self.tweet_url = "https://x.com" + tweet_links[0].get_attribute("href")
                    logger.info(f"TWITTER_POST_SUCCESS - Tweet URL: {self.tweet_url}")
                    return True

            except Exception as e:
                logger.error(f"TWITTER_POST_ERROR - Attempt {attempt}: {str(e)}")
                if attempt < max_retries:
                    time.sleep(10)
                    continue

        logger.error("TWITTER_POST_FAILED - All post attempts failed")
        return False

    def save_log(self, content: str, status: str) -> bool:
        """Save tweet log to vault."""
        try:
            logger.info("TWITTER_LOG - Saving to vault")

            log_file = LOGS_PATH / "Twitter_Log.md"

            log_entry = f"""
---

## Tweet Log Entry

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Tweet Content:**
```
{content}
```

**Tweet URL:** {self.tweet_url or 'N/A'}

**Status:** {status}

**Agent:** X_Twitter_MCP_Agent

---

"""

            # Append to log file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            logger.info(f"TWITTER_LOG_SUCCESS - Saved to {log_file}")
            return True

        except Exception as e:
            logger.error(f"TWITTER_LOG_ERROR - {str(e)}")
            return False

    def close_browser(self):
        """Close browser session."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()

            logger.info("TWITTER_BROWSER_CLOSED - Session ended")

        except Exception as e:
            logger.error(f"TWITTER_BROWSER_CLOSE_ERROR - {str(e)}")


class TwitterMCPServer:
    """MCP Server for Twitter browser automation."""

    def __init__(self):
        pass

    def autonomous_post(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Autonomous tweet posting using real Chrome profile.
        Retries until successful or max attempts reached.
        """
        agent = TwitterBrowserAgent()
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"TWITTER_AUTONOMOUS - Attempt {attempt}/{max_attempts}")

                # Step 1: Start browser with Chrome profile
                if not agent.start_browser():
                    continue

                # Step 2: Check login (no auto-login)
                if not agent.check_login():
                    agent.close_browser()
                    return {
                        "success": False,
                        "error": "Not logged in. Please log in to Twitter/X manually in Chrome first."
                    }

                # Step 3: Generate tweet
                tweet_content = agent.generate_tweet()

                # Step 4: Post tweet
                if not agent.post_tweet(tweet_content, dry_run=dry_run):
                    agent.close_browser()
                    continue

                # Step 5: Save log
                agent.save_log(tweet_content, "Posted" if not dry_run else "DRY_RUN")

                # Step 6: Close browser (no logout - keep session)
                agent.close_browser()

                logger.info("TWITTER_AUTONOMOUS_SUCCESS - Complete workflow executed")

                return {
                    "success": True,
                    "tweet_content": tweet_content,
                    "tweet_url": agent.tweet_url,
                    "message": "Tweet posted successfully" if not dry_run else "DRY RUN - Tweet not actually posted"
                }

            except Exception as e:
                logger.error(f"TWITTER_AUTONOMOUS_ERROR - Attempt {attempt}: {str(e)}")
                agent.close_browser()

                if attempt < max_attempts:
                    time.sleep(30)  # Wait before retry
                    continue

        return {
            "success": False,
            "error": "Failed to post tweet after all attempts"
        }


def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming MCP requests."""

    server = TwitterMCPServer()

    action = request.get('action')
    dry_run = request.get('dry_run', False)

    if action == 'autonomous_post':
        return server.autonomous_post(dry_run=dry_run)

    else:
        return {"success": False, "error": f"Unknown action: {action}"}


def main():
    """MCP Server main loop."""
    logger.info("TWITTER_BROWSER_SERVER_STARTED - Listening for MCP requests")

    try:
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = handle_mcp_request(request)
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {"success": False, "error": f"Invalid JSON: {str(e)}"}
                print(json.dumps(error_response), flush=True)

            except Exception as e:
                error_response = {"success": False, "error": f"Server error: {str(e)}"}
                print(json.dumps(error_response), flush=True)
                logger.error(f"TWITTER_BROWSER_SERVER_ERROR - {str(e)}")

    except KeyboardInterrupt:
        logger.info("TWITTER_BROWSER_SERVER_STOPPED - User interrupt")


if __name__ == "__main__":
    main()
