"""
Playwright Test Script - Verify Installation on Windows
Tests that Playwright can open Instagram and take screenshots
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import sys

def test_playwright():
    """Test Playwright installation by opening Instagram"""

    vault_path = Path("AI_Employee_Vault")
    logs_path = vault_path / "Logs"
    logs_path.mkdir(parents=True, exist_ok=True)

    screenshot_path = logs_path / "test.png"

    print("=" * 60)
    print("Testing Playwright Installation")
    print("=" * 60)

    try:
        with sync_playwright() as p:
            print("\n[1/5] Launching Chromium browser...")
            browser = p.chromium.launch(
                headless=False,  # Visible browser on Windows
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )

            print("[2/5] Creating browser context...")
            context = browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )

            print("[3/5] Opening new page...")
            page = context.new_page()

            print("[4/5] Navigating to Instagram.com...")
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)

            # Wait a bit for page to fully load
            page.wait_for_timeout(3000)

            print(f"[5/5] Taking screenshot -> {screenshot_path}")
            page.screenshot(path=str(screenshot_path), full_page=False)

            print("\n" + "=" * 60)
            print("SUCCESS! Playwright is working correctly")
            print("=" * 60)
            print(f"\nScreenshot saved to: {screenshot_path.absolute()}")
            print(f"File size: {screenshot_path.stat().st_size / 1024:.2f} KB")

            # Keep browser open for 3 seconds so user can see it
            page.wait_for_timeout(3000)

            browser.close()

            return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR: Playwright test failed")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure Chromium is installed: playwright install chromium")
        print("2. Check your internet connection")
        print("3. Try running as administrator")
        return False

if __name__ == "__main__":
    success = test_playwright()
    sys.exit(0 if success else 1)
