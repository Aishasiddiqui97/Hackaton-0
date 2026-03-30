#!/usr/bin/env python3
"""
Twitter/X Watcher - Gold Tier 2026
Monitors AI vault for "Post on Twitter" instructions and performs periodic mention checks.
Interval: 8 minutes (480 seconds)
"""

import os
import time
import requests
import logging
from pathlib import Path
from datetime import datetime

# Configuration
CHECK_INTERVAL = 480  # 8 minutes
MCP_URL = "http://localhost:3006"
VAULT_DIR = Path("AI_Employee_Vault")
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
LOGS_DIR = VAULT_DIR / "Logs"
LOG_FILE = LOGS_DIR / "Twitter_Watcher.log"

# Ensure log directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [TWITTER_WATCHER] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def check_mcp_health():
    try:
        response = requests.get(f"{MCP_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def process_pending_posts():
    """Scan Needs_Action for 'Post on Twitter' instructions."""
    logging.info("Checking for pending post instructions in Needs_Action...")
    
    if not NEEDS_ACTION_DIR.exists():
        return

    for task_file in NEEDS_ACTION_DIR.glob("*.md"):
        content = task_file.read_text(encoding='utf-8').lower()
        
        if "post on twitter" in content or "tweet this" in content:
            logging.info(f"Found post instruction in: {task_file.name}")
            
            # Extract content (very simple extraction for example)
            # In a real system, the reasoning engine would have prepared this.
            # Here we look for text between quotes or in a 'Content' field.
            tweet_text = ""
            if "content:" in content:
                tweet_text = content.split("content:")[1].split("\n")[0].strip()
            
            if tweet_text:
                logging.info(f"Attempting to post: {tweet_text[:50]}...")
                try:
                    res = requests.post(f"{MCP_URL}/post_tweet", json={"text": tweet_text}, timeout=30)
                    if res.status_code == 200 and res.json().get("success"):
                        logging.info("Tweet posted successfully!")
                        # Move task to Done or rename (simplified here)
                        done_path = VAULT_DIR / "Done" / task_file.name
                        os.makedirs(VAULT_DIR / "Done", exist_ok=True)
                        task_file.rename(done_path)
                    else:
                        logging.error(f"Post failed: {res.text}")
                except Exception as e:
                    logging.error(f"Error calling MCP: {e}")

def check_mentions_and_summary():
    """Trigger mentions check and summary generation via MCP."""
    logging.info("Triggering periodic mentions check and summary generation...")
    try:
        res = requests.get(f"{MCP_URL}/mentions", timeout=30)
        if res.status_code == 200:
            logging.info("Mentions check completed.")
        else:
            logging.error(f"Mentions check failed: {res.text}")
    except Exception as e:
        logging.error(f"Error calling MCP mentions: {e}")

def main_loop():
    logging.info("TWITTER WATCHER STARTED (8-minute cycle)")
    
    while True:
        if check_mcp_health():
            # 1. Process any pending post instructions from the vault
            process_pending_posts()
            
            # 2. Check for mentions and generate summary
            check_mentions_and_summary()
        else:
            logging.warning("Twitter MCP Server is offline. Retrying next cycle.")

        logging.info(f"Cycle complete. Waiting {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logging.info("Watcher stopped by user.")
