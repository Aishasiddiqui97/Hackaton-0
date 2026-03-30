import os
import time
import json
import logging
from datetime import datetime, timedelta

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
SIGNAL_DIR = os.path.join(VAULT_PATH, "Signals")
RETRY_FAILED_PATH = os.path.join(SIGNAL_DIR, "retry_failed.md")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("error_handler")

def retry_action(action_func, *args, max_retries=5, **kwargs):
    """Retries an action with exponential backoff (1s, 2s, 4s, 8s, 16s)."""
    retries = 0
    backoff = 1
    
    while retries < max_retries:
        try:
            return action_func(*args, **kwargs)
        except Exception as e:
            retries += 1
            if retries == max_retries:
                logger.error(f"Action failed after {max_retries} retries: {e}")
                _log_retry_failure(action_func.__name__, str(e))
                raise e
            
            logger.warning(f"Action failed (attempt {retries}/{max_retries}). Retrying in {backoff}s... Error: {e}")
            time.sleep(backoff)
            backoff *= 2 # Exponential backoff

def _log_retry_failure(action_name, error_msg):
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    with open(RETRY_FAILED_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n## 🚨 Retry Failed: {action_name}\n")
        f.write(f"- **Timestamp:** {datetime.now().isoformat()}\n")
        f.write(f"- **Error:** {error_msg}\n")
        f.write("- **Status:** Maximum retries reached. Human intervention required.\n")

def handle_platform_error(platform, error_type, error_msg):
    """
    Handles specific error types like AUTH or RATE_LIMIT.
    AUTH: Pause platform, write signal.
    RATE_LIMIT: Back off for cooldown.
    """
    if "auth" in error_type.lower() or "token" in error_msg.lower():
        _trigger_auth_alert(platform, error_msg)
    elif "rate" in error_type.lower() or "limit" in error_msg.lower():
        logger.warning(f"Rate limit hit on {platform}. Triggering cooldown.")
        # Cooldown logic (e.g. write to a status file that watchers read)
        _set_platform_status(platform, "COOLDOWN", expires_in=3600) # 1 hour default

def _trigger_auth_alert(platform, error_msg):
    signal_path = os.path.join(SIGNAL_DIR, f"AUTH_NEEDED_{platform.upper()}.md")
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    with open(signal_path, "w", encoding="utf-8") as f:
        f.write(f"# 🚨 AUTH REQUIRED: {platform.upper()}\n\n")
        f.write(f"The {platform} integration has paused due to an authentication error.\n\n")
        f.write(f"**Error Details:** {error_msg}\n")
        f.write(f"**Time:** {datetime.now().isoformat()}\n")
    logger.error(f"Auth alert triggered for {platform}")

def _set_platform_status(platform, status, expires_in=3600):
    status_file = os.path.join(VAULT_PATH, "Logs", "platform_status.json")
    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    
    current_status = {}
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            try: current_status = json.load(f)
            except: pass
            
    current_status[platform] = {
        "status": status,
        "until": (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    }
    
    with open(status_file, "w") as f:
        json.dump(current_status, f, indent=2)

def is_platform_available(platform):
    status_file = os.path.join(VAULT_PATH, "Logs", "platform_status.json")
    if not os.path.exists(status_file): return True
    
    with open(status_file, "r") as f:
        try: 
            status = json.load(f).get(platform)
            if not status: return True
            if status["status"] == "COOLDOWN":
                if datetime.now() < datetime.fromisoformat(status["until"]):
                    return False
        except: return True
    return True
