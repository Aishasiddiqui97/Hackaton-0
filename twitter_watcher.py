import os
import json
import time
import logging
import tweepy
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load credentials
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")
LOG_PATH = os.path.join(VAULT_PATH, "Logs", "twitter_watcher.log")
PROCESSED_IDS_PATH = os.path.join(VAULT_PATH, "Logs", "twitter_processed_ids.txt")

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
logger = logging.getLogger("twitter_watcher")

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
    filename = f"TWITTER_{data['type']}_{data['id']}.md"
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

class TwitterWatcher:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        self.me = self.client.get_me().data

    def poll_mentions(self, processed_ids):
        logger.info("Polling for Twitter mentions...")
        try:
            mentions = self.client.get_users_mentions(
                id=self.me.id, 
                max_results=20,
                tweet_fields=["created_at", "author_id", "text"]
            )
            if not mentions.data: return
            
            for tweet in mentions.data:
                tweet_id = str(tweet.id)
                if tweet_id in processed_ids: continue
                
                text = tweet.text
                keyword = check_keywords(text)
                if keyword:
                    # Get author username
                    author = self.client.get_user(id=tweet.author_id).data.username
                    create_action_file({
                        "type": "twitter_mention",
                        "id": tweet_id,
                        "from": f"@{author}",
                        "received": tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
                        "keyword": keyword,
                        "message": text
                    })
                mark_as_processed(tweet_id)
                processed_ids.add(tweet_id)
        except Exception as e:
            logger.error(f"Error polling mentions: {e}")

    def poll_dms(self, processed_ids):
        logger.info("Polling for Twitter DMs...")
        try:
            # v2 DMs use Client.get_direct_message_events()
            # Note: Requires 'dm.read' scope and often Basic tier.
            # v1.1 uses api.list_direct_messages()
            auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
            api = tweepy.API(auth)
            
            dms = api.get_direct_messages(count=20)
            for dm in dms:
                dm_id = str(dm.id)
                if dm_id in processed_ids: continue
                
                text = dm.message_create['message_data']['text']
                keyword = check_keywords(text)
                if keyword:
                    sender_id = dm.message_create['sender_id']
                    if sender_id == str(self.me.id): continue # Skip our own sent DMs
                    
                    sender_node = api.get_user(user_id=sender_id)
                    create_action_file({
                        "type": "twitter_dm",
                        "id": dm_id,
                        "from": f"@{sender_node.screen_name}",
                        "received": datetime.fromtimestamp(int(dm.created_timestamp)/1000).isoformat(),
                        "keyword": keyword,
                        "message": text
                    })
                mark_as_processed(dm_id)
                processed_ids.add(dm_id)
        except Exception as e:
            logger.error(f"Error polling DMs (Check Tier Permissions): {e}")

def main():
    logger.info("Starting Twitter Watcher...")
    watcher = TwitterWatcher()
    processed_ids = get_processed_ids()
    
    while True:
        watcher.poll_mentions(processed_ids)
        watcher.poll_dms(processed_ids)
        logger.info("Cycle complete. Sleeping for 3 minutes.")
        time.sleep(180)

if __name__ == "__main__":
    main()
