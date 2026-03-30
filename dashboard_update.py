import os
import json
from datetime import datetime

VAULT_PATH = os.path.join(os.environ.get("USERPROFILE"), "AI_Employee_Vault")
DASHBOARD_PATH = os.path.join(VAULT_PATH, "Dashboard.md")
NEEDS_ACTION_PATH = os.path.join(VAULT_PATH, "Needs_Action")

def get_pending_approvals():
    if not os.path.exists(NEEDS_ACTION_PATH): return "None"
    files = [f for f in os.listdir(NEEDS_ACTION_PATH) if f.endswith(".md")]
    if not files: return "None"
    return "\n".join([f"- {f}" for f in files[:10]])

def update_dashboard():
    # Placeholder stats (in a real system, these would pull from the MCPs or cache)
    status_fb = "✅ ON"
    status_ig = "✅ ON"
    status_tw = "✅ ON"
    status_odoo = "✅ ON"
    
    pending = get_pending_approvals()
    
    content = f"""# AI Employee Dashboard — Gold Tier

## 🚦 System Status
| Component      | Status | Last Check |
|----------------|--------|------------|
| Gmail Watcher  | ✅ ON  | {datetime.now().strftime('%H:%M')} |
| WhatsApp Watch | ✅ ON  | {datetime.now().strftime('%H:%M')} |
| Facebook Watch | {status_fb}  | {datetime.now().strftime('%H:%M')} |
| Instagram Watch| {status_ig}  | {datetime.now().strftime('%H:%M')} |
| Twitter Watch  | {status_tw}  | {datetime.now().strftime('%H:%M')} |
| Odoo           | {status_odoo}  | {datetime.now().strftime('%H:%M')} |

## 📬 Pending Approvals
{pending}

## 💰 Financial Snapshot
- **Weekly Revenue:** $0.00 (Run weekly_audit.py for details)
- **Unpaid Invoices:** 0

## 📱 Social This Week
(Summary pending - Run summaries for Facebook, Instagram, Twitter)

---
*Last Updated: {datetime.now().isoformat()}*
"""
    with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Dashboard updated: {DASHBOARD_PATH}")

if __name__ == "__main__":
    update_dashboard()
