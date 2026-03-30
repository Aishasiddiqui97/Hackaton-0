"""
Alternative launcher with FORCE GPU rendering
Use this if input box still doesn't appear with standard fix
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / "whatsapp_session"

def main():
    print("=" * 70)
    print("WhatsApp Agent - FORCE GPU Rendering Mode")
    print("=" * 70)
    print("This uses aggressive GPU flags to force input box rendering")
    print()

    with sync_playwright() as pw:
        print("[1/3] Launching browser with FORCE GPU mode...")

        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            channel="chrome",
            args=[
                # Anti-detection
                "--disable-blink-features=AutomationControlled",

                # Sandbox bypass (required for containers/root)
                "--no-sandbox",
                "--disable-setuid-sandbox",

                # FORCE GPU rendering (aggressive mode)
                "--use-gl=desktop",
                "--enable-gpu-rasterization",
                "--enable-native-gpu-memory-buffers",
                "--enable-accelerated-2d-canvas",
                "--enable-accelerated-video-decode",
                "--ignore-gpu-blocklist",

                # Memory & stability
                "--disable-dev-shm-usage",
                "--disable-software-rasterizer",

                # Network & rendering
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",

                # Extra rendering hints
                "--force-device-scale-factor=1",
                "--disable-blink-features=AutomationControlled",
            ],
            ignore_default_args=["--enable-automation"],
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        print("[2/3] Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

        print("[3/3] Waiting for WhatsApp to load...")
        print()
        print("👉 If QR code appears, please scan it")
        print("👉 Then click on ANY chat to test input box")
        print()

        try:
            page.wait_for_selector("#pane-side", timeout=90_000)
            print("✅ WhatsApp loaded!")
            print()
            print("=" * 70)
            print("MANUAL TEST:")
            print("1. Click on any chat in the browser window")
            print("2. Look at the BOTTOM of the chat window")
            print("3. You should see the typing area (input box)")
            print("4. Try typing something to verify it works")
            print("=" * 70)
            print()
            input("Press Enter when done testing (or Ctrl+C to exit)...")

        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("Troubleshooting:")
            print("1. Check internet connection")
            print("2. Ensure WhatsApp is active on your phone")
            print("3. Try clearing session: rm -rf whatsapp_session/")
            input("Press Enter to exit...")

        browser.close()
        print("\n✅ Browser closed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
