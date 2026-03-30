import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load credentials
load_dotenv()

FB_PAGE_ID = os.getenv("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
LOG_PATH = os.path.join(VAULT_PATH, "Logs", "facebook_watcher.log")
PROCESSED_IDS_PATH = os.path.join(VAULT_PATH, "Logs", "facebook_processed_ids.txt")

# Keywords
KEYWORDS = ['inquiry', 'price', 'cost', 'available', 'interested', 'buy', 'order', 'contact', 'help', 'support']

# Logging
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("facebook_watcher")

def get_processed_ids():
    if not os.path.exists(PROCESSED_IDS_PATH):
        return set()
    with open(PROCESSED_IDS_PATH, "r") as f:
        return set(line.strip() for line in f if line.strip())

def mark_as_processed(item_id):
    with open(PROCESSED_IDS_PATH, "a") as f:
        f.write(f"{item_id}\n")

def check_keywords(text):
    if not text: return None
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw in text_lower:
            return kw
    return None

def create_action_file(data):
    """Creates a markdown file in Vault/Needs_Action/."""
    filename = f"FACEBOOK_{data['type']}_{data['id']}.md"
    file_path = os.path.join(NEEDS_ACTION_PATH, filename)
    
    content = f"""---
type: {data['type']}
from: {data['from']}
post_id: {data.get('post_id', 'N/A')}
received: {data['received']}
keyword_matched: {data['keyword']}
status: pending
---
## Message Content
{data['message']}

## Suggested Actions
- [ ] Reply to {data['type'].split('_')[-1]}
- [ ] Flag as lead
- [ ] Archive
"""
    os.makedirs(NEEDS_ACTION_PATH, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Created action item: {filename}")

def poll_comments(processed_ids):
    logger.info("Polling for new comments...")
    try:
        url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/posts?fields=id,comments{{id,from,message,created_time}}&access_token={FB_ACCESS_TOKEN}"
        res = requests.get(url).json()
        
        for post in res.get("data", []):
            post_id = post.get("id")
            comments = post.get("comments", {}).get("data", [])
            for comment in comments:
                comment_id = comment.get("id")
                if comment_id in processed_ids: continue
                
                message = comment.get("message", "")
                keyword = check_keywords(message)
                if keyword:
                    create_action_file({
                        "type": "facebook_comment",
                        "id": comment_id,
                        "from": comment.get("from", {}).get("name", "Unknown"),
                        "post_id": post_id,
                        "received": comment.get("created_time"),
                        "keyword": keyword,
                        "message": message
                    })
                mark_as_processed(comment_id)
                processed_ids.add(comment_id)
    except Exception as e:
        logger.error(f"Error polling comments: {e}")

def poll_dms(processed_ids):
    logger.info("Polling for new DMs...")
    try:
        url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/conversations?fields=messages{{id,from,message,created_time}}&access_token={FB_ACCESS_TOKEN}"
        res = requests.get(url).json()
        
        for convo in res.get("data", []):
            messages = convo.get("messages", {}).get("data", [])
            for msg in messages:
                msg_id = msg.get("id")
                if msg_id in processed_ids: continue
                
                # Check if the message is from the user (sender is NOT the page)
                # Note: This is simplified. In production, check sender ID vs Page ID.
                sender = msg.get("from", {}).get("name", "")
                # If we don't have the page's name readily, we might need a separate call
                # but for now, we process all new messages then filter out our own.
                
                message = msg.get("message", "")
                keyword = check_keywords(message)
                if keyword:
                    create_action_file({
                        "type": "facebook_dm",
                        "id": msg_id,
                        "from": sender,
                        "received": msg.get("created_time"),
                        "keyword": keyword,
                        "message": message
                    })
                mark_as_processed(msg_id)
                processed_ids.add(msg_id)
    except Exception as e:
        logger.error(f"Error polling DMs: {e}")

def main():
    logger.info("Starting Facebook Watcher...")
    processed_ids = get_processed_ids()
    
    while True:
        poll_comments(processed_ids)
        poll_dms(processed_ids)
        logger.info("Cycle complete. Sleeping for 5 minutes.")
        time.sleep(300)

if __name__ == "__main__":
    main()
