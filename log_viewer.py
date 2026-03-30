import os
import json
import argparse
from datetime import datetime, timedelta

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
LOGS_DIR = os.path.join(VAULT_PATH, "Logs")

def load_logs(days=1):
    all_logs = []
    now = datetime.now()
    for i in range(days):
        date_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(LOGS_DIR, f"{date_str}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    all_logs.extend(json.load(f))
                except: pass
    return all_logs

def display_logs(logs):
    if not logs:
        print("No logs found for the selected criteria.")
        return
    
    print(f"{'Timestamp':<25} | {'Platform':<10} | {'Action':<15} | {'Result':<8}")
    print("-" * 65)
    for l in logs:
        print(f"{l['timestamp'][:23]:<25} | {l['platform']:<10} | {l['action_type']:<15} | {l.get('result', 'N/A'):<8}")
        if l.get('error_message'):
            print(f"  └─ ERROR: {l['error_message']}")

def main():
    parser = argparse.ArgumentParser(description="AI Employee Audit Log Viewer")
    parser.add_argument("--today", action="store_true", help="Show today's logs")
    parser.add_argument("--week", action="store_true", help="Show this week's logs")
    parser.add_argument("--failed", action="store_true", help="Show only failed actions")
    parser.add_argument("--platform", help="Filter by platform (facebook|instagram|twitter|gmail|odoo)")
    
    args = parser.parse_args()
    
    days = 1
    if args.week: days = 7
    
    logs = load_logs(days)
    
    if args.failed:
        logs = [l for l in logs if l.get("result") == "failed"]
    
    if args.platform:
        logs = [l for l in logs if l.get("platform") == args.platform]
        
    display_logs(logs)

if __name__ == "__main__":
    main()
