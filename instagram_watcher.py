import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load credentials
load_dotenv()

IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
LOG_PATH = os.path.join(VAULT_PATH, "Logs", "instagram_watcher.log")
PROCESSED_IDS_PATH = os.path.join(VAULT_PATH, "Logs", "instagram_processed_ids.txt")

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
logger = logging.getLogger("instagram_watcher")

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
    filename = f"INSTAGRAM_{data['type']}_{data['id']}.md"
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
    logger.info("Polling for new Instagram comments...")
    try:
        # Get recent media
        url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media?fields=id,comments{{id,text,from,timestamp}}&access_token={IG_ACCESS_TOKEN}"
        res = requests.get(url).json()
        
        for media in res.get("data", []):
            media_id = media.get("id")
            comments = media.get("comments", {}).get("data", [])
            for comment in comments:
                comment_id = comment.get("id")
                if comment_id in processed_ids: continue
                
                text = comment.get("text", "")
                keyword = check_keywords(text)
                if keyword:
                    create_action_file({
                        "type": "instagram_comment",
                        "id": comment_id,
                        "from": comment.get("from", {}).get("username", "Unknown"),
                        "post_id": media_id,
                        "received": comment.get("timestamp"),
                        "keyword": keyword,
                        "message": text
                    })
                mark_as_processed(comment_id)
                processed_ids.add(comment_id)
    except Exception as e:
        logger.error(f"Error polling Instagram comments: {e}")

def poll_dms(processed_ids):
    logger.info("Polling for new Instagram DMs...")
    try:
        # Instagram Direct Messages via Instagram Graph API
        url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/conversations?fields=messages{{id,from,text,created_time}}&platform=instagram&access_token={IG_ACCESS_TOKEN}"
        res = requests.get(url).json()
        
        for convo in res.get("data", []):
            messages = convo.get("messages", {}).get("data", [])
            for msg in messages:
                msg_id = msg.get("id")
                if msg_id in processed_ids: continue
                
                sender = msg.get("from", {}).get("username", "Unknown")
                text = msg.get("text", "")
                keyword = check_keywords(text)
                if keyword:
                    create_action_file({
                        "type": "instagram_dm",
                        "id": msg_id,
                        "from": sender,
                        "received": msg.get("created_time"),
                        "keyword": keyword,
                        "message": text
                    })
                mark_as_processed(msg_id)
                processed_ids.add(msg_id)
    except Exception as e:
        logger.error(f"Error polling Instagram DMs: {e}")

def main():
    logger.info("Starting Instagram Watcher...")
    processed_ids = get_processed_ids()
    
    while True:
        poll_comments(processed_ids)
        poll_dms(processed_ids)
        logger.info("Cycle complete. Sleeping for 5 minutes.")
        time.sleep(300)

if __name__ == "__main__":
    main()
