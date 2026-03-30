"""
Production-Ready WhatsApp Agent Launcher
Handles all edge cases and provides detailed logging
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    print("🔍 Checking dependencies...")

    try:
        import playwright
        print("✅ Playwright installed")
    except ImportError:
        print("❌ Playwright not found")
        print("   Run: pip install playwright")
        return False

    # Check if browsers are installed
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True
        )
        if "is already installed" in result.stdout or result.returncode == 0:
            print("✅ Chromium browser installed")
        else:
            print("⚠️  Chromium may not be installed")
            print("   Run: playwright install chromium")
    except Exception as e:
        print(f"⚠️  Could not verify browser installation: {e}")

    return True

def check_chrome_installed():
    """Check if Chrome is installed (preferred over Chromium)."""
    import platform
    system = platform.system()

    chrome_paths = {
        "Windows": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "Linux": [
            "/usr/bin/google-chrome",
            "/usr/bin/chrome",
            "/snap/bin/chromium",
        ],
        "Darwin": [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    }

    paths = chrome_paths.get(system, [])
    for path in paths:
        if Path(path).exists():
            print(f"✅ Chrome found at: {path}")
            return True

    print("⚠️  Chrome not found, will use Playwright's Chromium")
    return False

def main():
    print("=" * 70)
    print("WhatsApp Autonomous Agent - Production Launcher")
    print("=" * 70)
    print()

    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        sys.exit(1)

    # Step 2: Check Chrome
    check_chrome_installed()

    # Step 3: Check session directory
    session_dir = Path(__file__).parent / "whatsapp_session"
    if session_dir.exists():
        print(f"✅ Session directory exists: {session_dir}")
        print("   (QR scan not needed if session is valid)")
    else:
        print(f"⚠️  No session found. First run will require QR scan.")
        print(f"   Session will be saved to: {session_dir}")

    print("\n" + "=" * 70)
    print("Launch Options:")
    print("=" * 70)
    print("1. Test input box rendering (recommended first)")
    print("2. Single scan (manual mode)")
    print("3. Loop mode (autonomous agent)")
    print("4. Continuous autonomous agent (recommended for production)")
    print("5. Exit")
    print()

    choice = input("Select option (1-5): ").strip()

    if choice == "1":
        print("\n🚀 Launching input box test...")
        subprocess.run([sys.executable, "test_input_box.py"])

    elif choice == "2":
        print("\n🚀 Launching single scan mode...")
        subprocess.run([sys.executable, "whatsapp_agent.py", "--headful"])

    elif choice == "3":
        interval = input("Enter scan interval in seconds (default: 120): ").strip()
        interval = interval if interval else "120"
        print(f"\n🚀 Launching loop mode (scanning every {interval}s)...")
        subprocess.run([
            sys.executable, "whatsapp_agent.py",
            "--loop", "--interval", interval, "--headful"
        ])

    elif choice == "4":
        print("\n🚀 Launching continuous autonomous agent...")
        print("   This will run indefinitely until stopped (Ctrl+C)")
        subprocess.run([sys.executable, "autonomous_whatsapp_agent.py"])

    elif choice == "5":
        print("\n👋 Exiting...")
        sys.exit(0)

    else:
        print("\n❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
