#!/usr/bin/env python3
"""
Platinum Tier - Cloud Agent 
Path: /opt/ai-employee/cloud_agent.py
STRICT RULE: The Cloud Agent can ONLY create draft files. 
It NEVER executes real actions (no sending, no posting, no buying).
It NEVER stores WhatsApp sessions or banking credentials.
"""

import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Configuration
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))
UPDATES_DIR = os.path.join(VAULT_DIR, "Updates")

# Setup Logging
log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "cloud_agent.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cloud_agent")

class CloudAgent:
    def __init__(self):
        self.vault_path = Path(VAULT_DIR)
        
    def write_status(self):
        """Write status updates to /Updates/cloud_status.md"""
        status_file = self.vault_path / "Updates" / "cloud_status.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        status_content = f"""# Cloud Agent Status
**Last Update**: {timestamp}
**Mode**: DRAFT-ONLY / READ-ONLY
**Active Watchers**: Email, Social, Finance (Draft Mode)

The Cloud Agent is running successfully and waiting for events to generate drafts.
"""
        try:
            os.makedirs(status_file.parent, exist_ok=True)
            with open(status_file, "w", encoding="utf-8") as f:
                f.write(status_content)
            logger.info("Updated cloud_status.md")
        except Exception as e:
            logger.error(f"Failed to write status: {e}")

    def create_email_draft(self, to_address, subject, body, original_msg_id=None):
        """Create a draft email in the Pending_Approval folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"DRAFT_EMAIL_{timestamp}.md"
        draft_path = self.vault_path / "Pending_Approval" / "email" / filename
        
        content = f"""# 📧 Email Draft Approval Required
**To**: {to_address}
**Subject**: {subject}
**Original Message ID**: {original_msg_id or 'N/A'}
**Generated At**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status**: DRAFT (Created by Cloud Agent)

## Action Required
Move this file to `/Approved/` for the Local Agent to send it, or to `/Rejected/` to discard.

---
## Email Body
{body}
"""
        self._write_file(draft_path, content)
        logger.info(f"Created email draft: {filename}")

    def create_social_draft(self, platform, content):
        """Create a draft social post in the Pending_Approval folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"DRAFT_{platform.upper()}_{timestamp}.md"
        draft_path = self.vault_path / "Pending_Approval" / "social" / filename
        
        file_content = f"""# 📱 Social Post Draft Approval Required
**Platform**: {platform}
**Generated At**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status**: DRAFT (Created by Cloud Agent)

## Action Required
Move this file to `/Approved/` for the Local Agent to post it, or to `/Rejected/` to discard.

---
## Post Content
{content}
"""
        self._write_file(draft_path, file_content)
        logger.info(f"Created social draft: {filename}")

    def claim_task(self, source_path, category):
        """
        Move a file from Needs_Action to In_Progress/cloud_agent
        to signal that this agent is currently generating a draft for it.
        """
        try:
            source = Path(source_path)
            if not source.exists():
                return None
                
            dest_dir = self.vault_path / "In_Progress" / "cloud_agent"
            os.makedirs(dest_dir, exist_ok=True)
            
            dest = dest_dir / source.name
            source.rename(dest)
            logger.info(f"Claimed task: moved {source.name} to In_Progress/cloud_agent")
            return dest
        except Exception as e:
            logger.error(f"Failed to claim task {source_path}: {e}")
            return None

    def mark_task_done(self, in_progress_path):
        """Move an In_Progress file to Done after a draft is generated"""
        try:
            source = Path(in_progress_path)
            if not source.exists():
                return
                
            dest_dir = self.vault_path / "Done"
            os.makedirs(dest_dir, exist_ok=True)
            
            dest = dest_dir / source.name
            source.rename(dest)
            logger.info(f"Marked task done: {source.name}")
        except Exception as e:
            logger.error(f"Failed to mark task done {in_progress_path}: {e}")

    def _write_file(self, file_path, content):
        """Helper to write a file ensuring the directory exists"""
        try:
            os.makedirs(file_path.parent, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")

if __name__ == "__main__":
    agent = CloudAgent()
    agent.write_status()
    # Testing draft creation
    agent.create_email_draft("client@example.com", "Project Update", "Hello, here is the update...")
    agent.create_social_draft("Twitter", "The future is AI! #Automation")
    print("Cloud Agent script ran successfully in test mode. Drafts created.")
