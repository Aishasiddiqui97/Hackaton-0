#!/usr/bin/env python3
"""
Platinum Tier - Secrets Checker 
Path: /opt/ai-employee/secrets_checker.py
Can be run as an independent periodic scan or CI step to verify 
git history and active directory do not contain leaked secrets.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_for_leaks():
    vault_path = Path(VAULT_DIR)
    if not vault_path.exists():
        logging.error(f"Vault path not found: {vault_path}")
        return False

    suspicious_patterns = [
        ".env", "token.json", "credentials.json", 
        "id_rsa", ".pem", ".key", "whatsapp_session", "twitter_session"
    ]
    
    leaks_found = []
    
    # Simple recursive scan
    for root, _, files in os.walk(vault_path):
        if ".git" in root: continue
        
        for file in files:
            for pattern in suspicious_patterns:
                if pattern in file.lower() or file.endswith(pattern):
                    leaks_found.append(os.path.join(root, file))

    if leaks_found:
        logging.critical("🚨 SECURITY VIOLATION! Secret files found in Vault:")
        for leak in leaks_found:
            logging.critical(f"  - {leak}")
        logging.critical("Immediately remove these files and wipe git history if committed.")
        return False
    else:
        logging.info("✅ Security Check Passed: No sensitive files detected in Vault.")
        return True

if __name__ == "__main__":
    success = check_for_leaks()
    sys.exit(0 if success else 1)
