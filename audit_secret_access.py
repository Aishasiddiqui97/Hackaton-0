#!/usr/bin/env python3
"""
Platinum Tier - Audit Secret Access
Path: /opt/ai-employee/audit_secret_access.py

A secure wrapper to retrieve environment variables and log the exact
timestamp and process that requested them. Replaces os.getenv() for 
critical credentials.
"""

import os
import inspect
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))
log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)

# Separate dedicated audit log (highly sensitive)
audit_logger = logging.getLogger("security_audit")
audit_logger.setLevel(logging.INFO)
hdlr = logging.FileHandler(os.path.join(log_dir, "secrets_audit.log"))
hdlr.setFormatter(logging.Formatter('%(asctime)s - SECURITY_AUDIT - %(message)s'))
audit_logger.addHandler(hdlr)

def get_secret(key, default=None):
    """
    Secure retrieval of an environment variable.
    Logs which script/function requested the secret.
    """
    # Get the calling frame
    caller_frame = inspect.stack()[1]
    caller_filename = os.path.basename(caller_frame.filename)
    caller_function = caller_frame.function
    
    # Audit log
    audit_logger.info(f"Secret Requested: [{key}] by {caller_filename} -> {caller_function}()")
    
    val = os.getenv(key, default)
    
    if key.upper() == "DRY_RUN":
        audit_logger.info(f"DRY_RUN check returned: {val}")
        
    return val

if __name__ == "__main__":
    print("Testing Security Audit wrapper...")
    test_val = get_secret("TEST_API_KEY", "mock_key")
    _ = get_secret("DRY_RUN")
    print("Check AI_Employee_Vault/Logs/secrets_audit.log for results.")
