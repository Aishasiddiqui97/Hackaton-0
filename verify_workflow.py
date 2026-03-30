"""
Verification Script for Intelligent Message Management
"""
from pathlib import Path
import os
import subprocess
import sys

# Paths
VAULT_ROOT = Path(__file__).parent
INBOX_PATH = VAULT_ROOT / "00_Inbox" / "WhatsApp"
NEEDS_ACTION_PATH = VAULT_ROOT / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_ROOT / "02_Pending_Approvals" / "WhatsApp"

def create_test_message():
    """Create a dummy message with status: read."""
    test_file = INBOX_PATH / "2026-03-14_Simulated_User.md"
    content = """---
created: 2026-03-14 22:00:00
contact: Simulated User
category: Lead
status: unread
hot_lead: false
sensitive: false
tags: [whatsapp, test]
---

# WhatsApp Chat – Simulated User

| Field | Value |
|---|---|
| **Contact** | Simulated User |
| **Category** | Lead |
| **Timestamp** | 2026-03-14 22:00:00 |

---

## 💬 Conversation Summary

> **[Them]** I am interested in your pricing for AI chatbots. Can you send details?

---
_Logged by WhatsApp Business Agent_
"""
    test_file.write_text(content, encoding='utf-8')
    print(f"Created test message: {test_file.name}")
    return test_file

def verify_workflow():
    """Run the manager and check results."""
    # Ensure tool exists
    manager_script = VAULT_ROOT / "intelligent_message_manager.py"
    if not manager_script.exists():
        print("Error: manager script not found.")
        return

    # Run manager
    print("Running intelligent_message_manager.py...")
    subprocess.run([sys.executable, str(manager_script)], check=True)

    # Verify original file
    test_file = INBOX_PATH / "2026-03-14_Simulated_User.md"
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'status: Need Action' in content and 'need-action' in content:
        print("✅ Original file updated correctly (Status: Need Action).")
    else:
        print("❌ Original file NOT updated correctly.")
        print(content)

    # Verify Needs_Action file
    na_file = NEEDS_ACTION_PATH / "2026-03-14_Simulated_User.md"
    if na_file.exists():
        print(f"✅ File copied to Needs_Action: {na_file.name}")
    else:
        print("❌ File NOT found in Needs_Action.")

    # Verify pending approval file
    approval_file = PENDING_APPROVAL_PATH / "Approval_2026-03-14_Simulated_User.md"
    if approval_file.exists():
        print(f"✅ Pending approval file created: {approval_file.name}")
        print("--- Content Preview ---")
        print(approval_file.read_text(encoding='utf-8')[:200])
        print("-----------------------")
    else:
        print("❌ Pending approval file NOT created.")

if __name__ == "__main__":
    create_test_message()
    verify_workflow()
