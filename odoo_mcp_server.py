#!/usr/bin/env python3
"""
Platinum Tier - Odoo 19 MCP Server
Path: /opt/ai-employee/odoo_mcp_server.py
Exposes Odoo JSON-RPC tools to the Claude agent.
STRICT RULE: All cloud actions are DRAFT ONLY. 
They generate approval files in /Pending_Approval/odoo/.
"""

import os
import sys
import json
import logging
import xmlrpc.client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "secure_admin_password")

VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))

# Setup Logging
log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "odoo_mcp.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(log_dir, "odoo_mcp.log")), logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("odoo_mcp")

class OdooMCP:
    def __init__(self):
        self.common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        try:
            self.uid = self.common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
                logger.info("Successfully connected to Odoo 19.")
            else:
                logger.error("Failed to authenticate to Odoo.")
        except Exception as e:
            logger.error(f"Odoo connection exception: {e}")
            self.uid = None

    def _write_approval_file(self, odoo_type, odoo_id, details):
        """Creates the markdown file in /Pending_Approval/odoo/"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record_type = odoo_type.upper()
        filename = f"{record_type}_{timestamp}.md"
        filepath = os.path.join(VAULT_DIR, "Pending_Approval", "odoo", filename)
        
        content = f"""# 🏢 Odoo System Approval Required
**Type**: {record_type}
**Odoo ID**: {odoo_id}
**Generated At**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Action Required
This {odoo_type} is in DRAFT state in Odoo.
Move this file to `/Approved/` for the Local Agent to POST/VALIDATE it in Odoo.
Alternatively, move it to `/Rejected/` to cancel it.

---
## Details
{details}
"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Created approval file: {filepath}")
        except Exception as e:
            logger.error(f"Failed to write approval file: {e}")

    def create_invoice_draft(self, customer_id, amount, description):
        """Creates a DRAFT invoice in Odoo and generates an approval file."""
        if not self.uid: return {"success": False, "error": "Not connected to Odoo"}
        
        try:
            # Note: Minimal implementation. In a real Odoo setup you need product_id, account_id, etc.
            invoice_data = {
                'move_type': 'out_invoice',
                'partner_id': customer_id,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': description,
                        'price_unit': amount,
                        'quantity': 1.0,
                    })
                ]
            }
            invoice_id = self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, 'account.move', 'create', [invoice_data])
            
            details = f"Customer ID: {customer_id}\nAmount: ${amount}\nDescription: {description}"
            self._write_approval_file("INVOICE", invoice_id, details)
            
            return {"success": True, "invoice_id": invoice_id, "status": "draft_created", "file_generated": True}
        except Exception as e:
            logger.error(f"Failed to create draft invoice: {e}")
            return {"success": False, "error": str(e)}

    def create_expense_draft(self, amount, category, description):
        """Creates a DRAFT vendor bill/expense in Odoo and generates an approval file."""
        if not self.uid: return {"success": False, "error": "Not connected to Odoo"}
        
        try:
            # Outward expense mapped to in_invoice (Vendor Bill)
            expense_data = {
                'move_type': 'in_invoice',
                'invoice_line_ids': [
                    (0, 0, {
                        'name': f"{category}: {description}",
                        'price_unit': amount,
                        'quantity': 1.0,
                    })
                ]
            }
            expense_id = self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, 'account.move', 'create', [expense_data])
            
            details = f"Category: {category}\nAmount: ${amount}\nDescription: {description}"
            self._write_approval_file("EXPENSE", expense_id, details)
            
            return {"success": True, "expense_id": expense_id, "status": "draft_created", "file_generated": True}
        except Exception as e:
            logger.error(f"Failed to create draft expense: {e}")
            return {"success": False, "error": str(e)}

    def list_unpaid_invoices(self):
        """Read-only fetch of unpaid invoices"""
        if not self.uid: return {"success": False, "error": "Not connected to Odoo"}
        try:
            invoices = self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, 'account.move', 'search_read', 
                [[('payment_state', 'in', ['not_paid', 'partial']), ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]],
                {'fields': ['name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date_due']})
            return {"success": True, "invoices": invoices}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_monthly_revenue(self):
        """Read-only fetch of monthly revenue"""
        if not self.uid: return {"success": False, "error": "Not connected to Odoo"}
        try:
            current_month = datetime.now().strftime('%Y-%m-01')
            invoices = self.models.execute_kw(ODOO_DB, self.uid, ODOO_PASSWORD, 'account.move', 'search_read',
                [[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('invoice_date', '>=', current_month)]],
                {'fields': ['amount_total', 'amount_untaxed']})
            
            revenue = sum([inv['amount_untaxed'] for inv in invoices])
            return {"success": True, "monthly_revenue": revenue, "currency": "USD"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def handle_request(line):
    try:
        req = json.loads(line)
        mcp = OdooMCP()
        tool = req.get("tool")
        params = req.get("params", {})
        
        if tool == "create_invoice_draft":
            return mcp.create_invoice_draft(params.get("customer"), params.get("amount"), params.get("description"))
        elif tool == "create_expense_draft":
            return mcp.create_expense_draft(params.get("amount"), params.get("category"), params.get("description"))
        elif tool == "list_unpaid_invoices":
            return mcp.list_unpaid_invoices()
        elif tool == "get_monthly_revenue":
            return mcp.get_monthly_revenue()
        else:
            return {"error": f"Unknown tool: {tool}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip(): continue
        result = handle_request(line.strip())
        print(json.dumps(result), flush=True)
