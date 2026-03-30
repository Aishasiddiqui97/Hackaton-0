import os
import json
import subprocess
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
APPROVED_PATH = os.path.join(VAULT_PATH, "Approved")
DONE_PATH = os.path.join(VAULT_PATH, "Done")
LOG_PATH = os.path.join(VAULT_PATH, "Logs", "social_posts.json")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("content_scheduler")

def parse_draft(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("---")
    if len(parts) < 3: return None
    
    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            frontmatter[k.strip()] = v.strip()
    
    # Body is everything after the second ---
    body = parts[2].strip()
    return frontmatter, body

def call_mcp(platform, tool, params):
    """Calls the corresponding MCP server script."""
    script_map = {
        "facebook": "facebook_mcp_server.py",
        "instagram": "instagram_mcp_server.py",
        "twitter": "twitter_mcp_server.py",
        "linkedin": "mcp_servers/linkedin_server.py" # Assuming existing one
    }
    
    script_path = os.path.join(os.getcwd(), script_map.get(platform, ""))
    if not os.path.exists(script_path):
        logger.error(f"MCP script for {platform} not found at {script_path}")
        return {"error": "MCP server missing"}
    
    input_data = json.dumps({"tool": tool, "params": params})
    try:
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_data)
        if stderr: logger.error(f"MCP Stderr: {stderr}")
        return json.loads(stdout)
    except Exception as e:
        logger.error(f"Failed to call MCP: {e}")
        return {"error": str(e)}

import sys # Needed for sys.executable

def log_post(data):
    logs = []
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            try: logs = json.load(f)
            except: logs = []
    
    logs.append(data)
    with open(LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

def main():
    logger.info("Starting Content Scheduler...")
    if not os.path.exists(APPROVED_PATH): return
    
    now = datetime.now()
    files = [f for f in os.listdir(APPROVED_PATH) if f.startswith("DRAFT_")]
    
    for filename in files:
        file_path = os.path.join(APPROVED_PATH, filename)
        draft = parse_draft(file_path)
        if not draft: continue
        
        fm, body = draft
        scheduled_str = fm.get("scheduled_time")
        if not scheduled_str: continue
        
        try:
            scheduled_time = datetime.fromisoformat(scheduled_str.replace(" ", "T"))
        except:
            logger.error(f"Invalid date format in {filename}")
            continue
            
        if scheduled_time <= now:
            platform = fm.get("platform", "").lower()
            logger.info(f"Publishing {filename} to {platform}...")
            
            tool_map = {
                "facebook": "post_to_page",
                "instagram": "post_image",
                "twitter": "post_tweet",
                "linkedin": "post_to_linkedin" # Adjust based on actual server
            }
            
            params = {"message": body} if platform != "instagram" else {"caption": body, "image_path": fm.get("image_path")}
            if platform == "twitter": params = {"text": body, "media_path": fm.get("image_path")}
            if platform == "facebook": params = {"message": body, "image_path": fm.get("image_path")}
            
            result = call_mcp(platform, tool_map.get(platform), params)
            
            if result.get("success"):
                logger.info(f"Successfully published {filename}")
                log_post({
                    "timestamp": datetime.now().isoformat(),
                    "platform": platform,
                    "filename": filename,
                    "result": "success",
                    "post_id": result.get("id") or result.get("post_id")
                })
                # Move to Done
                os.makedirs(DONE_PATH, exist_ok=True)
                os.rename(file_path, os.path.join(DONE_PATH, filename))
            else:
                logger.error(f"Failed to publish {filename}: {result.get('error')}")
                log_post({
                    "timestamp": datetime.now().isoformat(),
                    "platform": platform,
                    "filename": filename,
                    "result": "failed",
                    "error": result.get("error")
                })

if __name__ == "__main__":
    main()
