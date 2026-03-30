"""
Quick test script to verify WhatsApp input box renders correctly
Run this to test the fix without running full agent
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def test_input_box():
    print("=" * 70)
    print("WhatsApp Input Box Render Test")
    print("=" * 70)

    with sync_playwright() as pw:
        print("\n[1/5] Launching browser with fixed args...")
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-software-rasterizer",
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
            ignore_default_args=["--enable-automation"],
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        print("[2/5] Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

        print("[3/5] Waiting for WhatsApp to load (scan QR if needed)...")
        try:
            page.wait_for_selector("#pane-side", timeout=90_000)
            print("✅ WhatsApp loaded successfully!")
        except:
            print("❌ WhatsApp did not load. Please scan QR code.")
            input("Press Enter after scanning QR code...")
            page.wait_for_selector("#pane-side", timeout=30_000)

        print("\n[4/5] Please manually click on ANY chat in the browser window...")
        print("(This test needs you to open a chat manually)")
        input("Press Enter after opening a chat...")

        print("[5/5] Checking if input box is visible...")
        time.sleep(2)

        # Check multiple selectors
        selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[data-testid="conversation-compose-box-input"]',
            'footer div[contenteditable="true"]',
        ]

        found = False
        for sel in selectors:
            try:
                input_box = page.query_selector(sel)
                if input_box and input_box.is_visible():
                    print(f"✅ SUCCESS! Input box found and visible: {sel}")

                    # Get bounding box to verify it's actually rendered
                    bbox = input_box.bounding_box()
                    if bbox:
                        print(f"   Position: x={bbox['x']}, y={bbox['y']}")
                        print(f"   Size: {bbox['width']}x{bbox['height']}px")
                        found = True
                        break
            except Exception as e:
                continue

        if not found:
            print("❌ FAILED! Input box not found or not visible")
            print("\nDebugging info:")
            try:
                footer = page.query_selector("footer")
                if footer:
                    print("✅ Footer element exists")
                    html = footer.inner_html()[:500]
                    print(f"Footer HTML preview: {html}")
                else:
                    print("❌ Footer element not found")
            except Exception as e:
                print(f"Error during debug: {e}")

        print("\n" + "=" * 70)
        print("Test complete. Check the browser window to verify input box.")
        print("=" * 70)
        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    try:
        test_input_box()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
