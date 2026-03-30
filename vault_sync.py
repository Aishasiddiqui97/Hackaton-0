#!/usr/bin/env python3
"""
Platinum Tier - Vault Sync Script (Cloud <-> Local)
Path: /opt/ai-employee/vault_sync.py (Cloud) or local path
Runs every 5 minutes to keep the AI Employee Vault in sync via Git.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Configuration
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))
IS_CLOUD = os.getenv("IS_CLOUD_VM", "false").lower() == "true"
SYNC_INTERVAL = 300 # 5 minutes

# Setup Logging
log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "vault_sync.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(f"vault_sync_{'cloud' if IS_CLOUD else 'local'}")

class VaultSynchronizer:
    def __init__(self):
        self.vault_path = Path(VAULT_DIR)
        os.chdir(self.vault_path)
        self.ensure_git_repo()

    def _run_git(self, cmd):
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                f"git {cmd}", shell=True, check=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def ensure_git_repo(self):
        """Check if we are in a valid git repository"""
        if not (self.vault_path / ".git").exists():
            logger.warning("No Git repository found. Initializing...")
            self._run_git("init")
            self._run_git("branch -M main")
            logger.info("Initialized empty Git repository. Please add a remote origin.")

    def enforce_sync_rules(self):
        """
        Enforce Platinum Tier Rules:
        - Single-writer rule: Only LOCAL writes to Dashboard.md directly.
        - Cloud writes updates ONLY to /Updates/ folder.
        """
        if IS_CLOUD:
            dashboard_path = self.vault_path / "Dashboard.md"
            if dashboard_path.exists():
                # Cloud should not be modifying Dashboard.md, revert if modified locally on cloud
                self._run_git("checkout -- Dashboard.md")

    def claim_by_move(self):
        """
        Claim-by-move rule:
        Any files in Needs_Action that the local/cloud agent is currently processing
        must be moved to In_Progress/<agent_name>/ to quickly signal it is claimed
        before syncing. This is usually done by the specific agents, but the sync 
        script commits these state changes.
        """
        # This function acts as a placeholder reminder of the rule.
        # The actual move is done by `cloud_agent.py` and `local_agent.py`
        pass

    def sync(self):
        """Perform exactly one Sync cycle"""
        logger.info("Starting sync cycle...")
        
        self.enforce_sync_rules()
        
        # 1. Pull changes first (rebase to avoid merge commits if possible)
        logger.info("Pulling latest changes from remote...")
        success, output = self._run_git("pull --rebase origin main")
        if not success:
            logger.error(f"Failed to pull: {output}")
            # Attempt to abort rebase if stuck
            self._run_git("rebase --abort")
            
        # 2. Add all local changes (honoring .gitignore)
        self._run_git("add .")
        
        # 3. Check if there's anything to commit
        success, status_output = self._run_git("status --porcelain")
        if status_output.strip() == "":
            logger.info("No local changes to commit. Sync complete.")
            return

        # 4. Commit and Push
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        identity = "Cloud_Agent" if IS_CLOUD else "Local_Agent"
        commit_message = f"Auto-Sync [{identity}] at {timestamp}"
        
        logger.info("Committing changes...")
        self._run_git(f'commit -m "{commit_message}"')
        
        logger.info("Pushing to remote...")
        success, output = self._run_git("push origin main")
        
        if success:
            logger.info("Sync cycle completed successfully.")
        else:
            logger.error(f"Failed to push: {output}")

    def run_forever(self):
        """Run the sync loop infinitely"""
        logger.info(f"Vault Sync daemon starting. Interval: {SYNC_INTERVAL}s. Role: {'Cloud' if IS_CLOUD else 'Local'}")
        while True:
            try:
                self.sync()
            except Exception as e:
                logger.critical(f"Unhandled exception in sync loop: {e}")
            
            time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    sync = VaultSynchronizer()
    sync.run_forever()
