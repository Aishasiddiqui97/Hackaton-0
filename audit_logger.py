import os
import json
import logging
from datetime import datetime, timedelta

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
LOGS_DIR = os.path.join(VAULT_PATH, "Logs")

def log_audit(action_type, actor, platform, target, parameters=None, approval_status="auto", approved_by="auto_rule", result="success", error_message=None):
    """Logs an action to the daily audit JSON file."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOGS_DIR, f"{today}.json")
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type, # email_send|social_post|payment|file_op
        "actor": actor, # claude_code|human|scheduler
        "platform": platform, # facebook|instagram|twitter|gmail|odoo
        "target": target, # post_id or recipient or file
        "parameters": parameters or {},
        "approval_status": approval_status, # auto|human_approved|human_rejected
        "approved_by": approved_by, # human|auto_rule
        "result": result, # success|failed|pending
        "error_message": error_message
    }
    
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    
    logs.append(entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)
    
    # Run cleanup and summary check
    _maintenance()

def _maintenance():
    """Handles 90-day retention and checks if a weekly summary is needed."""
    now = datetime.now()
    
    # 1. Retention (90 days)
    for f in os.listdir(LOGS_DIR):
        if f.endswith(".json"):
            try:
                file_date = datetime.strptime(f.replace(".json", ""), "%Y-%m-%d")
                if (now - file_date).days > 90:
                    os.remove(os.path.join(LOGS_DIR, f))
            except: pass

    # 2. Weekly Summary (if today is Sunday and summary doesn't exist)
    if now.weekday() == 6: # Sunday
        summary_file = os.path.join(LOGS_DIR, f"Weekly_Summary_{now.strftime('%Y-%m-%d')}.md")
        if not os.path.exists(summary_file):
            _generate_weekly_summary(summary_file)

def _generate_weekly_summary(output_path):
    now = datetime.now()
    summary = []
    total_actions = 0
    failures = 0
    
    for i in range(7):
        date_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(LOGS_DIR, f"{date_str}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                logs = json.load(f)
                total_actions += len(logs)
                for l in logs:
                    if l["result"] == "failed": failures += 1
                    summary.append(l)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Weekly Audit Summary - {now.strftime('%Y-%m-%d')}\n\n")
        f.write(f"- **Total Actions:** {total_actions}\n")
        f.write(f"- **Failed Actions:** {failures}\n")
        f.write(f"- **Success Rate:** {round((total_actions-failures)/max(total_actions,1)*100, 2)}%\n\n")
        f.write("## Detailed Logs (Last 7 Days)\n")
        f.write("| Timestamp | Platform | Action | Result |\n")
        f.write("|-----------|----------|--------|--------|\n")
        for entry in summary[:50]: # Top 50 recent
            f.write(f"| {entry['timestamp']} | {entry['platform']} | {entry['action_type']} | {entry['result']} |\n")
