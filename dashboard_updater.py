#!/usr/bin/env python3
"""
Platinum Tier - Dashboard Updater
Path: ~/AI_Employee_Vault/dashboard_updater.py (Runs on Local Machine)
Runs periodically to aggregate logs, statuses, and pending files
into a single source-of-truth Dashboard.md
"""

import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))
UPDATE_INTERVAL = 120 # 2 minutes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("dashboard_updater")

class DashboardUpdater:
    def __init__(self):
        self.vault_path = Path(VAULT_DIR)
        self.dashboard_path = self.vault_path / "Dashboard.md"
        self.updates_dir = self.vault_path / "Updates"
        self.pending_dir = self.vault_path / "Pending_Approval"
        self.logs_dir = self.vault_path / "Logs"

    def aggregate_data(self):
        data = {
            "heartbeat": "[Offline]",
            "pending_count": 0,
            "drafts_today": 0,
            "failed_auth": "None detected",
            "unpaid_invoices_count": 0,
            "unpaid_invoices_amount": "$0.00",
            "mtd_revenue": "$0.00",
            "pending_files": [],
            "recent_activity": []
        }
        
        # 1. Read Heartbeat
        heartbeat_file = self.updates_dir / "heartbeat.md"
        if heartbeat_file.exists():
            with open(heartbeat_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("**Last Check**:"):
                        data["heartbeat"] = line.split(":", 1)[1].strip()
                        break

        # 2. Count Pending Approvals
        if self.pending_dir.exists():
            for root, _, files in os.walk(self.pending_dir):
                for file in files:
                    if file.endswith(".md"):
                        data["pending_files"].append(file)
            data["pending_count"] = len(data["pending_files"])
            
        # 3. Read Executions Log (Last 5 activities)
        today = datetime.now().strftime("%Y-%m-%d")
        exec_log = self.logs_dir / f"{today}_execution.json"
        if exec_log.exists():
            try:
                with open(exec_log, "r") as f:
                    logs = json.load(f)
                    data["drafts_today"] = len(logs) # Rough proxy for today's drafts/actions
                    for log in logs[-5:]:
                        ts = log.get("timestamp", "").split("T")[1][:5]
                        status = "✅" if log.get("status") in ["SUCCESS", "SIMULATED_SUCCESS"] else "❌"
                        action = log.get("action_type", "ACTION")
                        data["recent_activity"].append(f"- [{ts}] {status} {action}")
            except: pass
            
        # 4. Read Security Audit Logs for failed auth
        audit_log = self.logs_dir / "secrets_audit.log"
        if audit_log.exists():
            with open(audit_log, "r") as f:
                content = f.read()
                data["failed_auth"] = str(content.count("VIOLATION") + content.count("Failed"))
                
        if not data["recent_activity"]:
            data["recent_activity"].append("- No recent actions today.")
            
        return data

    def write_dashboard(self, data):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        pending_str = "\n".join([f"- `{f}`" for f in data["pending_files"]]) if data["pending_files"] else "*(No items pending approval)*"
        activity_str = "\n".join(data["recent_activity"])
        
        content = f"""# 🌟 Personal AI Employee - Platinum Dashboard
**Last Updated**: {timestamp}

## ☁️ Cloud Agent Status
- **Last heartbeat**: `{data['heartbeat']}`
- **Pending approvals**: `{data['pending_count']}`
- **Actions/Drafts today**: `{data['drafts_today']}`

## 🔐 Security Status  
- **Last credential rotation**: `Configured Manually`
- **Failed auth attempts**: `{data['failed_auth']}`

## 📊 Odoo Summary
- **Unpaid invoices**: `{data['unpaid_invoices_count']}` `{data['unpaid_invoices_amount']}`
- **MTD Revenue**: `{data['mtd_revenue']}`

## ✅ Approval Queue
{pending_str}

---
## 🏃 Activity Log
{activity_str}
"""
        with open(self.dashboard_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Dashboard updated at {timestamp}")

    def run_forever(self):
        logger.info("Dashboard Updater started.")
        while True:
            try:
                data = self.aggregate_data()
                self.write_dashboard(data)
                time.sleep(UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Failed to update dashboard: {e}")
                time.sleep(60)

if __name__ == "__main__":
    updater = DashboardUpdater()
    updater.run_forever()
