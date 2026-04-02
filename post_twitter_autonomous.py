#!/usr/bin/env python3
"""
Autonomous Twitter Poster
Single command - Login, Create Post with Hashtags, Post, Show Result, Logout
"""

import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import urllib.parse

# Add vault to path
sys.path.insert(0, str(Path(__file__).parent / "AI_Employee_Vault" / "twitter"))
from session_manager import TwitterSessionManager

load_dotenv()

# Chrome profile
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA_DIR", r"C:\Users\hp\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = os.getenv("CHROME_PROFILE", "Default")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")

# Vault paths
VAULT_PATH = Path("AI_Employee_Vault")
LOGS_PATH = VAULT_PATH / "Logs"
LOGS_PATH.mkdir(parents=True, exist_ok=True)


def random_delay(min_ms=8000, max_ms=15000):
    """Random human-like delay"""
    delay = random.randint(min_ms, max_ms) / 1000
    time.sleep(delay)


def random_mouse_move(page):
    """Random mouse movements"""
    try:
        x = random.randint(100, 500)
        y = random.randint(100, 500)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.1, 0.3))
    except:
        pass


def generate_tweet_with_hashtags():
    """Generate tweet content with hashtags"""
    tweets = [
        "AI is revolutionizing how businesses operate across the globe. Digital employees work 24/7 without breaks, automate complex tasks, and scale instantly to meet demand. The future belongs to organizations that embrace Human + AI collaboration. This is not just automation - it's transformation. 🚀\n\n#AI #Automation #DigitalEmployee #FutureOfWork #AIAgent #BusinessTransformation #Innovation",

        "Building autonomous AI agents that actually deliver measurable results is an art and science combined. When implemented correctly with proper oversight and clear objectives, they completely transform business operations, reduce costs, and unlock new possibilities. The ROI speaks for itself. 💡\n\n#AIAutomation #BusinessAutomation #DigitalFTE #Innovation #TechTrends #AIStrategy #DigitalTransformation",

        "The best AI employees don't replace talented humans - they amplify human potential by handling repetitive, time-consuming tasks so your team can focus on strategy, creativity, and high-value work. That's the real productivity unlock that forward-thinking companies are discovering. ⚡\n\n#AI #Productivity #Automation #WorkSmart #DigitalTransformation #FutureOfWork #AIInnovation",

        "Imagine an employee that never sleeps, never makes errors, learns continuously, and scales infinitely without additional overhead. That's exactly what AI automation brings to modern businesses. The question isn't if you'll adopt it, but when. 🤖\n\n#AIEmployee #BusinessGrowth #Automation #Innovation #FutureTech #AIRevolution #SmartBusiness",

        "We built a Digital FTE that autonomously monitors operations, posts on social media, generates detailed reports, and handles customer inquiries - all with complete logging and human oversight. This isn't science fiction. This is happening right now. 🎯\n\n#AI #Automation #DigitalFTE #AIAgent #TechInnovation #BusinessAutomation #AITransformation"
    ]

    tweet = random.choice(tweets)
    
    # Append unique ID to bypass duplicate content filters
    unique_id = f" [ID:{random.randint(1000, 9999)}]"
    
    # Ensure under 250 characters total (safe margin)
    limit = 250 - len(unique_id)
    if len(tweet) > limit:
        tweet = tweet[:limit-3] + "..."
    
    tweet = tweet + unique_id
    return tweet


def post_tweet_autonomous():
    """Main autonomous posting function"""

    print("=" * 70)
    print("🤖 AUTONOMOUS TWITTER POSTER")
    print("=" * 70)
    print()

    session_manager = TwitterSessionManager()

    with sync_playwright() as p:
        # Launch Chrome with real profile
        profile_path = os.path.join(CHROME_USER_DATA, CHROME_PROFILE)
        print(f"[1/7] 🚀 Opening Chrome with your profile...")
        print(f"      Profile: {profile_path}")

        context = p.chromium.launch_persistent_context(
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
            no_viewport=True # Uses real window size
        )

        # Add stealth
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.pages[0] if context.pages else context.new_page()

        try:
            # Step 1: Check login
            print("\n[2/7] 🔐 Checking login status...")

            # Navigate with better timeout and wait condition
            print("      - Navigating to Twitter...")
            try:
                page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=90000)
            except Exception as nav_error:
                print(f"      ⚠️  First navigation attempt failed: {nav_error}")
                print("      - Retrying with longer timeout...")
                page.goto("https://twitter.com/home", wait_until="load", timeout=120000)

            # Wait for page to settle
            print("      - Waiting for page to load...")
            time.sleep(5)

            # Check if logged in
            print("      - Verifying login status...")
            logged_in = False

            # Check for home feed indicators
            indicators = [
                '[data-testid="primaryColumn"]',
                '[data-testid="SideNav_NewTweet_Button"]',
                '[aria-label="Home"]',
            ]

            for indicator in indicators:
                try:
                    if page.locator(indicator).is_visible(timeout=5000):
                        logged_in = True
                        break
                except:
                    continue

            if not logged_in:
                print("\n❌ NOT LOGGED IN!")
                print("Please log into Twitter in Chrome first:")
                print("1. Open Chrome")
                print("2. Go to https://twitter.com")
                print("3. Log in")
                print("4. Close Chrome")
                print("5. Run this script again")

                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"twitter_not_logged_in_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")

                context.close()
                return False

            print("      ✅ Already logged in!")

            # Step 2: Generate tweet
            print("\n[3/7] 📝 Generating tweet with unique ID...")
            tweet_content = generate_tweet_with_hashtags()
            
            # Add Timestamp to start for absolute uniqueness
            timestamp_str = datetime.now().strftime("%H:%M:%S")
            tweet_content = f"[{timestamp_str}] {tweet_content}"
            
            print(f"      Content: {tweet_content[:80]}...")
            print(f"      Length: {len(tweet_content)} characters")

            # Step 3: Navigate to home (if not already there)
            print("\n[4/7] 🏠 Ensuring we're on Twitter home...")
            current_url = page.url
            if "home" not in current_url:
                print("      - Navigating to home...")
                page.goto("https://twitter.com/home", wait_until="domcontentloaded", timeout=90000)
                time.sleep(3)
            else:
                print("      - Already on home page")

            random_delay(3000, 5000)

            # Step 4: Open Sidebar Modal on Home Page
            print("\n[5/7] 📤 Opening modal composer from sidebar...")
            
            # Ensure we're on home first
            if "home" not in page.url.lower():
                page.goto("https://twitter.com/home", wait_until="load", timeout=60000)
            
            time.sleep(3)
            
            # Click the Sidebar "Post" button
            try:
                sidebar_post_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]:visible').first
                sidebar_post_btn.click()
                print("      - Sidebar Post button clicked.")
            except:
                print("      ⚠️ Sidebar button not found, trying keyboard 'n'...")
                page.keyboard.press("n")

            time.sleep(2)

            # --- Overlay Handling ---
            print("      - Checking for overlays...")
            try:
                page.evaluate("() => { document.querySelectorAll('[data-testid=\"twc-cc-mask\"], .css-175oi2r.r-1pi2tsx').forEach(m => m.style.display = 'none'); }")
            except: pass

            # TARGET MODAL TEXTAREA
            print("      - Filling tweet content in modal...")
            tweet_input = page.locator('div[data-testid="tweetTextarea_0"]:visible, div[role="textbox"]:visible').first
            tweet_input.wait_for(state="visible", timeout=30000)
            
            # --- FORCE FOCUS ---
            tweet_input.scroll_into_view_if_needed()
            tweet_input.click(delay=100)
            time.sleep(0.5)
            tweet_input.fill("")
            time.sleep(0.5)
            
            # Type the content
            print("      - Typing content...")
            for char in tweet_content:
                page.keyboard.type(char, delay=random.randint(10, 30))
            
            # Final triggers
            time.sleep(0.8)
            page.keyboard.press("Space")
            page.keyboard.press("Backspace")
            time.sleep(1)

            # Wait for Post button
            print("      - Waiting for Post button...")
            publish_button_selector = '[data-testid="tweetButton"]:visible:not([aria-disabled="true"])'
            
            posted = False
            try:
                page.wait_for_selector(publish_button_selector, timeout=30000)
                print("      ✅ Post button is now enabled!")
                
                # FINAL CLICK
                print("      🚀 Clicking Post button...")
                publish_button = page.locator('[data-testid="tweetButton"]:visible').first
                
                # Use real mouse click
                box = publish_button.bounding_box()
                if box:
                    page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                else:
                    publish_button.click()
                
                # Wait for redirection/closure
                page.wait_for_selector('div[data-testid="tweetTextarea_0"]', state="detached", timeout=12000)
                print("      ✅ Tweet posted successfully!")
                posted = True

            except:
                print("      ⚠️ Modal still open, re-focusing and trying Keyboard Fallback...")
                
                # --- CRITICAL: RE-FOCUS TEXTAREA BEFORE KEYBOARD ---
                input_box = page.locator('div[data-testid="tweetTextarea_0"]:visible, div[role="textbox"]:visible').first
                try:
                    ibox = input_box.bounding_box()
                    if ibox:
                        # Click middle of textarea to be 100% sure of focus
                        page.mouse.click(ibox["x"] + ibox["width"]/2, ibox["y"] + ibox["height"]/4)
                    else:
                        input_box.focus()
                except:
                    input_box.focus()
                
                time.sleep(0.5)
                # BACKUP SUBMIT
                page.keyboard.press("Control+Enter")
                
                try:
                    page.wait_for_selector('div[data-testid="tweetTextarea_0"]', state="detached", timeout=12000)
                    print("      ✅ Tweet posted via keyboard fallback!")
                    posted = True
                except:
                    print("      ❌ Still failed — possibly blocked or wrong focus")
                    posted = False

            # 🔥 FINAL STATUS OUTPUT
            print("\n" + "="*70)
            if posted:
                print("✅ FULLY POSTED")
                print("="*70)
            else:
                print("❌ POSTING FAILED")
                print("="*70)
                context.close()
                return False

            # Step 5: Capture tweet URL (only if posted)
            if posted:
                print("\n[6/7] 🔗 Capturing tweet URL...")
            try:
                # Clear toast or SENT banner if it's blocking
                page.evaluate("() => { const layers = document.querySelector('#layers'); if(layers) layers.style.pointerEvents = 'none'; }")
                time.sleep(1)
                
                profile_link = page.locator('[data-testid="AppTabBar_Profile_Link"]').first
                random_mouse_move(page)
                time.sleep(random.uniform(1.5, 3.0))
                
                # Use JS click if locator.click is intercepted
                try:
                    profile_link.click(timeout=10000)
                except:
                    print("      ⚠️  Profile click intercepted, using fallback JS click...")
                    page.evaluate("document.querySelector('[data-testid=\"AppTabBar_Profile_Link\"]').click()")
                
                random_delay(5000, 8000)
                
                # Reset pointer events for actual article links
                page.evaluate("() => { const layers = document.querySelector('#layers'); if(layers) layers.style.pointerEvents = 'auto'; }")

                # Get first tweet link
                tweet_url = None
                tweet_links = page.locator('article a[href*="/status/"]').all()
                if tweet_links:
                    tweet_url = "https://x.com" + tweet_links[0].get_attribute("href")
                    print(f"      ✅ Tweet URL: {tweet_url}")
                else:
                    tweet_url = "URL not captured (check profile manually)"
                    print("      ⚠️  Could not capture URL automatically")
            except Exception as url_error:
                tweet_url = "URL capture failed (tweet posted successfully)"
                print(f"      ⚠️  URL capture error: {url_error}")
                print("      ℹ️  Tweet was posted, but URL couldn't be captured")

            # Step 6: Save log
            print("\n[7/7] 💾 Saving to log...")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file = LOGS_PATH / "Twitter_Log.md"

            log_entry = f"""
---

## Tweet Posted - Autonomous

**Date:** {timestamp}

**Tweet Content:**
```
{tweet_content}
```

**Tweet URL:** {tweet_url}

**Status:** Posted Successfully

**Method:** Autonomous Chrome Profile

---

"""

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            print(f"      ✅ Logged to: {log_file}")

            # Show result
            print("\n" + "=" * 70)
            print("✅ SUCCESS! TWEET POSTED")
            print("=" * 70)
            print(f"\n📝 Tweet Content:\n{tweet_content}")
            print(f"\n🔗 Tweet URL: {tweet_url}")
            print(f"\n📊 Length: {len(tweet_content)} characters")
            print(f"📅 Posted: {timestamp}")

            # Optional: Logout
            print("\n" + "=" * 70)
            print("\n🔒 Logout Options:")
            print("   y = Logout now")
            print("   n = Stay logged in (recommended for automation)")
            logout_choice = input("\nYour choice (y/n): ").strip().lower()

            if logout_choice == 'y':
                print("\n[LOGOUT] Logging out...")
                try:
                    page.goto("https://twitter.com/logout", wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)

                    # Confirm logout
                    logout_confirm = page.locator('[data-testid="confirmationSheetConfirm"]')
                    if logout_confirm.is_visible(timeout=3000):
                        logout_confirm.click()
                        time.sleep(2)
                        print("         ✅ Logged out successfully")
                    else:
                        print("         ⚠️  Logout confirmation not found")
                except Exception as e:
                    print(f"         ⚠️  Logout error: {e}")
            else:
                print("\n[SKIP] ✅ Staying logged in for future automation")

            print("\n[CLOSE] Closing browser in 5 seconds...")
            page.wait_for_timeout(5000)

            context.close()
            return True

        except Exception as e:
            print(f"\n❌ ERROR: {e}")

            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"twitter_error_{timestamp}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")

            print("\n[CLOSE] Browser will stay open for 60 seconds for debugging...")
            page.wait_for_timeout(60000)

            context.close()
            return False


if __name__ == "__main__":
    print("\n🤖 Starting Autonomous Twitter Poster...")
    print("⚠️  Make sure Chrome is closed before running!\n")

    try:
        success = post_tweet_autonomous()

        if success:
            print("\n" + "=" * 70)
            print("🎉 AUTONOMOUS POSTING COMPLETE!")
            print("=" * 70)
            sys.exit(0)
        else:
            print("\n" + "=" * 70)
            print("❌ POSTING FAILED")
            print("=" * 70)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
