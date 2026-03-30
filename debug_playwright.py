
from playwright.sync_api import sync_playwright
import os

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Opening google.com...")
        page.goto("https://google.com", timeout=30000)
        print("Success: " + page.title())
        browser.close()
except Exception as e:
    print(f"Playwright Debug Error: {e}")
