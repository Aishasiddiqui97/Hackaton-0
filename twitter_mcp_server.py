import os
import json
import sys
import logging
import tweepy
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load credentials
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
SIGNAL_PATH = os.path.join(VAULT_PATH, "Signals", "twitter_auth_needed.md")

# Logging setup
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "twitter_mcp.log")),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("twitter_mcp")

def _handle_auth_error(e):
    logger.error(f"Twitter Auth Error: {e}")
    try:
        os.makedirs(os.path.dirname(SIGNAL_PATH), exist_ok=True)
        with open(SIGNAL_PATH, "w") as f:
            f.write(f"# 🚨 Twitter Authentication Needed\n\nError: {e}\nDetected at: {datetime.now().isoformat()}")
    except: pass

class TwitterMCP:
    def __init__(self):
        try:
            # v2 Client for most operations
            self.client = tweepy.Client(
                bearer_token=BEARER_TOKEN,
                consumer_key=API_KEY,
                consumer_secret=API_SECRET,
                access_token=ACCESS_TOKEN,
                access_token_secret=ACCESS_SECRET,
                wait_on_rate_limit=True
            )
            # v1.1 API for media upload
            auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
            self.api = tweepy.API(auth)
            self.me = self.client.get_me().data
        except Exception as e:
            _handle_auth_error(e)
            self.client = None
            self.api = None
            self.me = None

    def post_tweet(self, text, media_path=None):
        """Posts tweet, optionally with image/video."""
        try:
            media_ids = []
            if media_path and os.path.exists(media_path):
                media = self.api.media_upload(media_path)
                media_ids.append(media.media_id)
            
            response = self.client.create_tweet(text=text, media_ids=media_ids if media_ids else None)
            return {"success": True, "id": response.data["id"]}
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {"success": False, "error": str(e)}

    def post_thread(self, tweets_list):
        """Posts a thread (list of connected tweets)."""
        try:
            last_tweet_id = None
            published_ids = []
            for tweet_text in tweets_list:
                response = self.client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=last_tweet_id
                )
                last_tweet_id = response.data["id"]
                published_ids.append(last_tweet_id)
            return {"success": True, "ids": published_ids}
        except Exception as e:
            logger.error(f"Error posting thread: {e}")
            return {"success": False, "error": str(e)}

    def get_account_summary(self):
        """Returns: followers, following, tweets this week, total impressions, top tweet."""
        try:
            user = self.client.get_user(id=self.me.id, user_fields=["public_metrics"])
            metrics = user.data.public_metrics
            
            # Get tweets this week
            start_time = datetime.utcnow() - timedelta(days=7)
            tweets = self.client.get_users_tweets(
                id=self.me.id,
                start_time=start_time.isoformat() + "Z",
                tweet_fields=["public_metrics"]
            )
            
            tweets_data = tweets.data if tweets.data else []
            total_impressions = sum(t.public_metrics.get("impression_count", 0) for t in tweets_data)
            
            top_tweet = "None"
            max_likes = -1
            for t in tweets_data:
                likes = t.public_metrics.get("like_count", 0)
                if likes > max_likes:
                    max_likes = likes
                    top_tweet = t.text[:100] + "..."

            return {
                "success": True,
                "followers": metrics["followers_count"],
                "following": metrics["following_count"],
                "tweets_this_week": len(tweets_data),
                "total_impressions": total_impressions,
                "top_tweet": top_tweet
            }
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return {"success": False, "error": str(e)}

    def get_mentions(self, limit=20):
        """Returns recent @mentions needing reply."""
        try:
            mentions = self.client.get_users_mentions(id=self.me.id, max_results=limit)
            return {"success": True, "mentions": [m.data for m in mentions.data] if mentions.data else []}
        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
            return {"success": False, "error": str(e)}

    def search_keyword_mentions(self, keyword):
        """Searches tweets mentioning a keyword related to my business."""
        try:
            # Note: v2 Free tier search is limited to recent/sampled
            query = f"{keyword} -is:retweet"
            tweets = self.client.search_recent_tweets(query=query, max_results=10)
            return {"success": True, "tweets": [t.data for t in tweets.data] if tweets.data else []}
        except Exception as e:
            logger.error(f"Error searching keyword: {e}")
            return {"success": False, "error": str(e)}

    def reply_to_tweet(self, tweet_id, text):
        """Replies to a specific tweet."""
        try:
            response = self.client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)
            return {"success": True, "id": response.data["id"]}
        except Exception as e:
            logger.error(f"Error replying to tweet: {e}")
            return {"success": False, "error": str(e)}

def handle_request(line):
    try:
        req = json.loads(line)
        mcp = TwitterMCP()
        if not mcp.client: return {"error": "Twitter client initialization failed"}
        
        tool = req.get("tool")
        params = req.get("params", {})
        
        if tool == "post_tweet":
            return mcp.post_tweet(**params)
        elif tool == "post_thread":
            return mcp.post_thread(**params)
        elif tool == "get_account_summary":
            return mcp.get_account_summary()
        elif tool == "get_mentions":
            return mcp.get_mentions(**params)
        elif tool == "search_keyword_mentions":
            return mcp.search_keyword_mentions(**params)
        elif tool == "reply_to_tweet":
            return mcp.reply_to_tweet(**params)
        else:
            return {"error": f"Unknown tool: {tool}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip(): continue
        result = handle_request(line.strip())
        print(json.dumps(result), flush=True)
