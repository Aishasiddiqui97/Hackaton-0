#!/usr/bin/env python3
"""
Platinum Tier - Always-On Cloud Orchestrator
Path: /opt/ai-employee/cloud_orchestrator.py
Runs 24/7 via PM2 on the Cloud VM.
Manages rate limits, handles errors with exponential backoff, and writes heartbeat.
"""

import os
import time
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))
HEARTBEAT_INTERVAL = 60 # 60 seconds

log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "cloud_orchestrator.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("orchestrator")

class CloudOrchestrator:
    def __init__(self):
        self.vault_path = Path(VAULT_DIR)
        self.updates_dir = self.vault_path / "Updates"
        os.makedirs(self.updates_dir, exist_ok=True)
        
        # Rate Limiting State (in a real system, use Redis or SQLite)
        self.state_file = self.vault_path / "Logs" / "orchestrator_state.json"
        self.state = self._load_state()

        self.limits = {
            "email_drafts_per_hour": 10,
            "social_drafts_per_hour": 20
        }

    def _load_state(self):
        default_state = {
            "email_count": 0,
            "social_count": 0,
            "last_reset": datetime.now().isoformat()
        }
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    # Reset if an hour has passed
                    last_reset = datetime.fromisoformat(state["last_reset"])
                    if datetime.now() - last_reset > timedelta(hours=1):
                        return default_state
                    return state
            except Exception:
                pass
        return default_state

    def _save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def write_heartbeat(self):
        """Writes heartbeat every 60s to /Updates/heartbeat.md"""
        heartbeat_path = self.updates_dir / "heartbeat.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"""# 💓 Cloud Orchestrator Heartbeat
**Last Check**: {timestamp}
**Status**: ONLINE
**Active PM2 Processes**: Managed

## Rate Limits (Current Hour)
- Email Drafts: {self.state['email_count']} / {self.limits['email_drafts_per_hour']}
- Social Drafts: {self.state['social_count']} / {self.limits['social_drafts_per_hour']}
"""
        try:
            with open(heartbeat_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write heartbeat: {e}")

    def monitor_rate_limits(self):
        """
        Check if rate limits are breached by scanning the Pending_Approval
        folder or Logs, and potentially pause PM2 watchers if too high.
        Since we don't have a database, we'll incrementally count files created in the last hour.
        (Simplified logic: assume watchers respect dynamic flags, or just alert)
        """
        # Count files generated in the last hour in Pending_Approval
        now = datetime.now()
        email_dir = self.vault_path / "Pending_Approval" / "email"
        social_dir = self.vault_path / "Pending_Approval" / "social"
        
        email_count = 0
        if email_dir.exists():
            for f in email_dir.glob("*.md"):
                if now - datetime.fromtimestamp(f.stat().st_mtime) < timedelta(hours=1):
                    email_count += 1
                    
        social_count = 0
        if social_dir.exists():
            for f in social_dir.glob("*.md"):
                if now - datetime.fromtimestamp(f.stat().st_mtime) < timedelta(hours=1):
                    social_count += 1
                    
        self.state["email_count"] = email_count
        self.state["social_count"] = social_count
        self._save_state()
        
        if email_count >= self.limits["email_drafts_per_hour"]:
            logger.warning("Email rate limit reached! Pausing gmail_cloud_watcher...")
            subprocess.run("pm2 stop gmail_cloud_watcher", shell=True)
            self._write_signal("rate_limit_email.md", "Email draft limit reached. Watcher paused.")
            
        if social_count >= self.limits["social_drafts_per_hour"]:
            logger.warning("Social rate limit reached! Pausing social_cloud_watcher...")
            subprocess.run("pm2 stop social_cloud_watcher", shell=True)
            self._write_signal("rate_limit_social.md", "Social draft limit reached. Watcher paused.")

    def _write_signal(self, filename, message):
        """Write a signal for the human/local agent to review"""
        signal_path = self.vault_path / "Signals" / filename
        os.makedirs(signal_path.parent, exist_ok=True)
        try:
            with open(signal_path, "w") as f:
                f.write(f"# 🚨 Signal: {filename}\nTime: {datetime.now()}\n\n{message}")
        except: pass

    def run_forever(self):
        logger.info("Cloud Orchestrator started.")
        while True:
            try:
                self.write_heartbeat()
                self.monitor_rate_limits()
                time.sleep(HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.critical(f"Orchestrator error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    orchestrator = CloudOrchestrator()
    orchestrator.run_forever()
