import os
import json
import sys
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

FB_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FB_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
SIGNAL_PATH = os.path.join(VAULT_PATH, "Signals", "facebook_auth_needed.md")

# Logging setup
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "facebook_mcp.log")),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("facebook_mcp")

def _handle_api_error(error_data):
    """Handles API errors and writes auth alerts to the vault if needed."""
    error_msg = str(error_data)
    logger.error(f"Facebook API Error: {error_msg}")
    
    # Check for authentication errors (code 190)
    if '"code": 190' in error_msg or "expired" in error_msg.lower() or "invalid" in error_msg.lower():
        try:
            os.makedirs(os.path.dirname(SIGNAL_PATH), exist_ok=True)
            with open(SIGNAL_PATH, "w") as f:
                f.write(f"# 🚨 Facebook Authentication Needed\n\n")
                f.write(f"The Facebook Page Access Token has expired or is invalid.\n")
                f.write(f"**Detected at:** `{datetime.now().isoformat()}`\n\n")
                f.write(f"Please follow the [API Setup Guides](file:///C:/Users/hp/.gemini/antigravity/brain/6f06e457-34d5-46a1-a5ec-4f428aec1c41/api_setup_guides.md) to refresh the token.")
            logger.warning(f"Auth alert written to {SIGNAL_PATH}")
        except Exception as e:
            logger.error(f"Failed to write signal file: {e}")

class FacebookMCP:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"

    def post_to_page(self, message, image_path=None):
        """Posts text or image+text to the Facebook Business Page."""
        try:
            if image_path and os.path.exists(image_path):
                url = f"{self.base_url}/{FB_PAGE_ID}/photos"
                with open(image_path, "rb") as img:
                    files = {"source": img}
                    data = {"message": message, "access_token": FB_ACCESS_TOKEN}
                    response = requests.post(url, data=data, files=files)
            else:
                url = f"{self.base_url}/{FB_PAGE_ID}/feed"
                data = {"message": message, "access_token": FB_ACCESS_TOKEN}
                response = requests.post(url, data=data)
            
            res_json = response.json()
            if response.status_code != 200:
                _handle_api_error(res_json)
                return {"success": False, "error": res_json}
            
            return {"success": True, "id": res_json.get("id"), "post_id": res_json.get("post_id")}
        except Exception as e:
            _handle_api_error(e)
            return {"success": False, "error": str(e)}

    def get_page_summary(self):
        """Returns: total likes, reach last 7 days, top post this week, engagement rate."""
        try:
            # 1. Basic Info
            url = f"{self.base_url}/{FB_PAGE_ID}?fields=fan_count,engagement&access_token={FB_ACCESS_TOKEN}"
            basic_info = requests.get(url).json()
            if "error" in basic_info:
                _handle_api_error(basic_info)
                return {"success": False, "error": basic_info}

            # 2. Insights for Reach
            since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            insights_url = f"{self.base_url}/{FB_PAGE_ID}/insights?metric=page_impressions_unique&period=day&since={since}&access_token={FB_ACCESS_TOKEN}"
            insights = requests.get(insights_url).json()
            
            total_reach = 0
            if "data" in insights and len(insights["data"]) > 0:
                for entry in insights["data"][0].get("values", []):
                    total_reach += entry.get("value", 0)

            # 3. Recent Posts for top performer
            posts_url = f"{self.base_url}/{FB_PAGE_ID}/posts?fields=id,message,engagement,likes.summary(true),comments.summary(true)&limit=20&access_token={FB_ACCESS_TOKEN}"
            posts = requests.get(posts_url).json().get("data", [])
            
            top_post = "No posts this week"
            max_engagement = -1
            engagement_sum = 0
            
            for p in posts:
                # Engagement estimate: likes + comments + shares (shares not in field above but engagement covers some)
                likes = p.get("likes", {}).get("summary", {}).get("total_count", 0)
                comments = p.get("comments", {}).get("summary", {}).get("total_count", 0)
                eng = likes + comments
                engagement_sum += eng
                if eng > max_engagement:
                    max_engagement = eng
                    top_post = p.get("message", p.get("id"))[:50] + "..."

            engagement_rate = round((engagement_sum / max(total_reach, 1)) * 100, 2) if total_reach > 0 else 0

            return {
                "success": True,
                "total_likes": basic_info.get("fan_count", 0),
                "reach_last_7_days": total_reach,
                "top_post_this_week": top_post,
                "engagement_rate": f"{engagement_rate}%"
            }
        except Exception as e:
            _handle_api_error(e)
            return {"success": False, "error": str(e)}

    def get_recent_posts(self, limit=10):
        """Returns list of recent posts with likes/comments/shares."""
        try:
            url = f"{self.base_url}/{FB_PAGE_ID}/posts?fields=id,message,created_time,likes.summary(true),comments.summary(true),shares&limit={limit}&access_token={FB_ACCESS_TOKEN}"
            res = requests.get(url).json()
            if "error" in res:
                _handle_api_error(res)
                return {"success": False, "error": res}
            
            clean_posts = []
            for p in res.get("data", []):
                clean_posts.append({
                    "id": p.get("id"),
                    "message": p.get("message", ""),
                    "timestamp": p.get("created_time"),
                    "likes": p.get("likes", {}).get("summary", {}).get("total_count", 0),
                    "comments": p.get("comments", {}).get("summary", {}).get("total_count", 0),
                    "shares": p.get("shares", {}).get("count", 0)
                })
            return {"success": True, "posts": clean_posts}
        except Exception as e:
            _handle_api_error(e)
            return {"success": False, "error": str(e)}

    def schedule_post(self, message, scheduled_time, image_path=None):
        """Schedules a post for future publishing."""
        try:
            # scheduled_time can be ISO string or timestamp
            if isinstance(scheduled_time, str):
                try:
                    dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    ts = int(dt.timestamp())
                except:
                    return {"success": False, "error": "Invalid ISO timestamp format"}
            else:
                ts = int(scheduled_time)

            data = {
                "message": message,
                "published": "false",
                "scheduled_publish_time": ts,
                "access_token": FB_ACCESS_TOKEN
            }
            
            if image_path and os.path.exists(image_path):
                url = f"{self.base_url}/{FB_PAGE_ID}/photos"
                with open(image_path, "rb") as img:
                    files = {"source": img}
                    response = requests.post(url, data=data, files=files)
            else:
                url = f"{self.base_url}/{FB_PAGE_ID}/feed"
                response = requests.post(url, data=data)
            
            res_json = response.json()
            if response.status_code != 200:
                _handle_api_error(res_json)
                return {"success": False, "error": res_json}
            
            return {"success": True, "id": res_json.get("id"), "scheduled_time": ts}
        except Exception as e:
            _handle_api_error(e)
            return {"success": False, "error": str(e)}

def handle_request(line):
    try:
        req = json.loads(line)
        mcp = FacebookMCP()
        tool = req.get("tool")
        params = req.get("params", {})
        
        if tool == "post_to_page":
            return mcp.post_to_page(**params)
        elif tool == "get_page_summary":
            return mcp.get_page_summary()
        elif tool == "get_recent_posts":
            return mcp.get_recent_posts(**params)
        elif tool == "schedule_post":
            return mcp.schedule_post(**params)
        else:
            return {"error": f"Unknown tool: {tool}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Simple test mode
        mcp = FacebookMCP()
        print("Testing get_page_summary...")
        print(json.dumps(mcp.get_page_summary(), indent=2))
    else:
        # Standard MCP loop
        for line in sys.stdin:
            if not line.strip(): continue
            result = handle_request(line.strip())
            print(json.dumps(result), flush=True)
