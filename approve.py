#!/usr/bin/env python3
"""
Platinum Tier - HITL Approval CLI
Path: ~/AI_Employee_Vault/approve.py
Command-line tool to review, approve, or reject drafts from the Cloud Agent.
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))

class ApproverCLI:
    def __init__(self):
        self.vault_path = Path(VAULT_DIR)
        self.pending_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.rejected_dir = self.vault_path / "Rejected"

    def list_pending(self):
        """List all pending drafts across categories"""
        print("\n📋 PENDING APPROVALS:")
        print("="*50)
        
        count = 0
        if not self.pending_dir.exists():
            print("No pending directory found.")
            return

        for category in ["email", "social", "finance", "odoo"]:
            cat_dir = self.pending_dir / category
            if cat_dir.exists():
                files = list(cat_dir.glob("*.md"))
                if files:
                    print(f"\n📂 [{category.upper()}]")
                    for f in files:
                        print(f"  - {f.name}")
                        count += 1
                        
        if count == 0:
            print("\n✅ Queue is empty! No pending approvals.")
        else:
            print(f"\nTotal pending: {count}")
            print("Use: python approve.py --approve <filename> OR python approve.py --reject <filename>")

    def _find_file(self, filename):
        """Find a file in the pending subdirectories"""
        for category in ["email", "social", "finance", "odoo"]:
            path = self.pending_dir / category / filename
            if path.exists():
                return path
        return None

    def show_diff(self, filename):
        """Show what will be executed before confirming"""
        filepath = self._find_file(filename)
        if not filepath:
            print(f"❌ File '{filename}' not found in Pending_Approval.")
            return False

        print(f"\n🔍 REVIEWING: {filename}")
        print("="*50)
        with open(filepath, "r", encoding="utf-8") as f:
            print(f.read())
        print("="*50)
        return filepath

    def approve(self, filename):
        """Move file to Approved directory"""
        filepath = self.show_diff(filename)
        if not filepath: return
        
        confirm = input(f"\n⚠️  Are you sure you want to APPROVE '{filename}' for execution? (y/N): ")
        if confirm.lower() == 'y':
            os.makedirs(self.approved_dir, exist_ok=True)
            dest = self.approved_dir / filename
            filepath.rename(dest)
            print(f"✅ Approved. {filename} moved to /Approved/ for Local Agent execution.")
        else:
            print("⏳ Approval cancelled.")

    def reject(self, filename):
        """Move file to Rejected directory"""
        filepath = self._find_file(filename)
        if not filepath:
            print(f"❌ File '{filename}' not found in Pending_Approval.")
            return
            
        confirm = input(f"\n🗑️  Are you sure you want to REJECT '{filename}'? (y/N): ")
        if confirm.lower() == 'y':
            os.makedirs(self.rejected_dir, exist_ok=True)
            dest = self.rejected_dir / filename
            filepath.rename(dest)
            print(f"🚫 Rejected. {filename} moved to /Rejected/.")
        else:
            print("⏳ Rejection cancelled.")

def main():
    parser = argparse.ArgumentParser(description="Platinum Tier HITL Approval CLI")
    parser.add_argument("--list", action="store_true", help="List all pending approvals")
    parser.add_argument("--approve", metavar="FILENAME", help="Approve a specific file")
    parser.add_argument("--reject", metavar="FILENAME", help="Reject a specific file")
    
    args = parser.parse_args()
    cli = ApproverCLI()
    
    if args.list:
        cli.list_pending()
    elif args.approve:
        cli.approve(args.approve)
    elif args.reject:
        cli.reject(args.reject)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
