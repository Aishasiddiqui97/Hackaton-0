#!/usr/bin/env python3
"""
Twitter/X Browser Automation MCP Server - Gold Tier
Autonomous browser-based Twitter posting with retry logic
"""

import json
import logging
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

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


class TwitterBrowserAgent:
    """Browser automation agent for Twitter/X posting."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.tweet_url = None

    def start_browser(self) -> bool:
        """Initialize browser session."""
        try:
            logger.info("TWITTER_BROWSER_START - Initializing Playwright")

            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,  # Set to True for production
                args=['--start-maximized']
            )

            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            self.page = context.new_page()

            logger.info("TWITTER_BROWSER_SUCCESS - Browser initialized")
            return True

        except Exception as e:
            logger.error(f"TWITTER_BROWSER_ERROR - Failed to start browser: {str(e)}")
            return False

    def login(self, max_retries: int = 3) -> bool:
        """Login to Twitter/X account with retry logic."""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"TWITTER_LOGIN_ATTEMPT - Attempt {attempt}/{max_retries}")

                # Navigate to login page
                self.page.goto("https://x.com/login", wait_until="networkidle", timeout=30000)
                time.sleep(2)

                # Enter email/username
                logger.info("TWITTER_LOGIN - Entering email")
                email_input = self.page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
                email_input.fill(self.email)
                time.sleep(1)

                # Click Next
                next_button = self.page.locator('text="Next"').first
                next_button.click()
                time.sleep(2)

                # Enter password
                logger.info("TWITTER_LOGIN - Entering password")
                password_input = self.page.wait_for_selector('input[name="password"]', timeout=10000)
                password_input.fill(self.password)
                time.sleep(1)

                # Click Login
                login_button = self.page.locator('text="Log in"').first
                login_button.click()

                # Wait for home timeline
                logger.info("TWITTER_LOGIN - Waiting for home timeline")
                self.page.wait_for_url("https://x.com/home", timeout=15000)
                time.sleep(3)

                # Verify login success
                if "home" in self.page.url:
                    logger.info("TWITTER_LOGIN_SUCCESS - Logged in successfully")
                    return True

            except PlaywrightTimeout as e:
                logger.error(f"TWITTER_LOGIN_TIMEOUT - Attempt {attempt}: {str(e)}")
                if attempt < max_retries:
                    time.sleep(10)
                    continue

            except Exception as e:
                logger.error(f"TWITTER_LOGIN_ERROR - Attempt {attempt}: {str(e)}")
                if attempt < max_retries:
                    time.sleep(10)
                    continue

        logger.error("TWITTER_LOGIN_FAILED - All login attempts failed")
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

        import random
        tweet = random.choice(tweets)

        # Ensure under 280 characters
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."

        logger.info(f"TWITTER_GENERATE - Tweet: {tweet[:50]}...")
        return tweet

    def post_tweet(self, content: str, max_retries: int = 3) -> bool:
        """Post tweet with retry logic."""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"TWITTER_POST_ATTEMPT - Attempt {attempt}/{max_retries}")

                # Click "Post" button to open composer
                logger.info("TWITTER_POST - Opening tweet composer")
                post_button = self.page.locator('[data-testid="SideNav_NewTweet_Button"]').first
                post_button.click()
                time.sleep(2)

                # Enter tweet text
                logger.info("TWITTER_POST - Entering tweet content")
                tweet_input = self.page.locator('[data-testid="tweetTextarea_0"]').first
                tweet_input.fill(content)
                time.sleep(2)

                # Click Post button
                logger.info("TWITTER_POST - Publishing tweet")
                publish_button = self.page.locator('[data-testid="tweetButtonInline"]').first
                publish_button.click()

                # Wait for tweet to be posted
                time.sleep(5)

                # Capture tweet URL from timeline
                logger.info("TWITTER_POST - Capturing tweet URL")

                # Navigate to profile to find latest tweet
                profile_link = self.page.locator('[data-testid="AppTabBar_Profile_Link"]').first
                profile_link.click()
                time.sleep(3)

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

    def logout(self) -> bool:
        """Logout from Twitter/X."""
        try:
            logger.info("TWITTER_LOGOUT - Logging out")

            # Click profile menu
            self.page.locator('[data-testid="AppTabBar_Profile_Link"]').first.click()
            time.sleep(1)

            # Click logout
            self.page.locator('text="Log out"').first.click()
            time.sleep(1)

            # Confirm logout
            self.page.locator('[data-testid="confirmationSheetConfirm"]').first.click()
            time.sleep(2)

            logger.info("TWITTER_LOGOUT_SUCCESS - Logged out")
            return True

        except Exception as e:
            logger.error(f"TWITTER_LOGOUT_ERROR - {str(e)}")
            return False

    def close_browser(self):
        """Close browser session."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            logger.info("TWITTER_BROWSER_CLOSED - Session ended")

        except Exception as e:
            logger.error(f"TWITTER_BROWSER_CLOSE_ERROR - {str(e)}")


class TwitterMCPServer:
    """MCP Server for Twitter browser automation."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def autonomous_post(self) -> Dict[str, Any]:
        """
        Autonomous tweet posting with Ralph Wiggum loop.
        Retries until successful or max attempts reached.
        """
        agent = TwitterBrowserAgent(self.email, self.password)
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"TWITTER_AUTONOMOUS - Attempt {attempt}/{max_attempts}")

                # Step 1: Start browser
                if not agent.start_browser():
                    continue

                # Step 2: Login
                if not agent.login():
                    agent.close_browser()
                    continue

                # Step 3: Generate tweet
                tweet_content = agent.generate_tweet()

                # Step 4: Post tweet
                if not agent.post_tweet(tweet_content):
                    agent.logout()
                    agent.close_browser()
                    continue

                # Step 5: Save log
                agent.save_log(tweet_content, "Posted")

                # Step 6: Logout
                agent.logout()

                # Step 7: Close browser
                agent.close_browser()

                logger.info("TWITTER_AUTONOMOUS_SUCCESS - Complete workflow executed")

                return {
                    "success": True,
                    "tweet_content": tweet_content,
                    "tweet_url": agent.tweet_url,
                    "message": "Tweet posted successfully"
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

    # Get credentials from environment or request
    email = os.getenv('TWITTER_EMAIL', request.get('email'))
    password = os.getenv('TWITTER_PASSWORD', request.get('password'))

    if not email or not password:
        return {
            "success": False,
            "error": "Twitter credentials not provided"
        }

    server = TwitterMCPServer(email, password)

    action = request.get('action')

    if action == 'autonomous_post':
        return server.autonomous_post()

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
