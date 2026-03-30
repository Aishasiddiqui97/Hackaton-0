#!/usr/bin/env python3
"""
Platinum Tier - Gmail Cloud Watcher
Path: /opt/ai-employee/gmail_cloud_watcher.py
Poller that checks Gmail via Gmail API, creates an analysis in Needs_Action,
and then immediately uses CloudAgent to draft a response in Pending_Approval.
"""

import os
import time
import base64
import logging
from datetime import datetime
from dotenv import load_dotenv

# Try importing the Google API client
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

from cloud_agent import CloudAgent

load_dotenv()
CHECK_INTERVAL = int(os.getenv("GMAIL_CHECK_INTERVAL", "60"))
VAULT_DIR = os.getenv("VAULT_SYNC_DIR", os.path.join(os.getcwd(), "AI_Employee_Vault"))

# Setup Logging
log_dir = os.path.join(VAULT_DIR, "Logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "gmail_cloud_watcher.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gmail_cloud_watcher")

class GmailCloudWatcher:
    def __init__(self):
        self.agent = CloudAgent()
        self.creds = None
        self.service = None
        self.last_check = datetime.now()
        
        # In the cloud, credentials must be pre-authorized 
        # (transferred from Local during initial setup, but in .gitignore!)
        self.token_path = os.path.join(os.getcwd(), "token.json")
        self.credentials_path = os.path.join(os.getcwd(), "credentials.json")
        self.processed_file = os.path.join(log_dir, "processed_emails_cloud.txt")
        self.processed_ids = self._load_processed()

    def _load_processed(self):
        try:
            if os.path.exists(self.processed_file):
                with open(self.processed_file, "r") as f:
                    return set(f.read().splitlines())
        except Exception:
            pass
        return set()

    def _save_processed(self, msg_id):
        self.processed_ids.add(msg_id)
        try:
            with open(self.processed_file, "a") as f:
                f.write(f"{msg_id}\n")
        except Exception as e:
            logger.error(f"Failed to save processed ID {msg_id}: {e}")

    def authenticate(self):
        """Authenticate with Gmail API"""
        if not GOOGLE_API_AVAILABLE:
            logger.warning("Google API client not installed. Mocking authentication.")
            return True
            
        try:
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, ['https://www.googleapis.com/auth/gmail.readonly'])
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    logger.error("No valid Gmail token found. Need to auth locally and transfer token.json to Cloud VM.")
                    
                    # Create a signal for the Local Agent that the Cloud Agent needs Auth
                    signal_path = os.path.join(VAULT_DIR, "Signals", "auth_needed.md")
                    os.makedirs(os.path.dirname(signal_path), exist_ok=True)
                    with open(signal_path, "w") as f:
                        f.write(f"# 🚨 Gmail Auth Needed on Cloud\nToken missing or invalid at {datetime.now()}. Transfer `token.json` to VM.")
                    return False
                    
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return False

    def check_new_emails(self):
        """Poll Gmail for new unread messages"""
        if not self.service:
            # Mock behavior if auth fails (e.g. during Hackathon without real token on VM yet)
            # Create a mock draft for demonstration purposes if triggered by a test file
            test_trigger = os.path.join(VAULT_DIR, "Needs_Action", "email", "test_trigger.md")
            if os.path.exists(test_trigger):
                logger.info("Found test_trigger.md. Creating mock email draft.")
                self.agent.create_email_draft("vip_client@example.com", "Project Status Update", "Hello, the project is on track. Please review the attached.\n\nBest,\nYour Digital FTE", "msg_mock_123")
                os.remove(test_trigger)
                return
            return

        try:
            results = self.service.users().messages().list(userId='me', q='is:unread').execute()
            messages = results.get('messages', [])

            for message in messages:
                msg_id = message['id']
                if msg_id in self.processed_ids:
                    continue

                logger.info(f"Processing new email: {msg_id}")
                msg = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                
                # Use Cloud Agent to DRAFT a reply!
                # STRICT RULE: NEVER SEND, ONLY DRAFT
                logger.info(f"Drafting reply for email from {sender} - {subject}")
                
                # In a real scenario, Claude API would be invoked here to generate the body based on the email content
                # We are generating a static generic draft string for the mock/demo
                draft_body = f"Hello {sender.split('<')[0].strip()},\n\nI have received your email regarding '{subject}'. I am prioritizing this and will have an update for you shortly.\n\nBest Regards,\nAI Assistant"
                
                self.agent.create_email_draft(
                    to_address=sender,
                    subject=f"Re: {subject}",
                    body=draft_body,
                    original_msg_id=msg_id
                )
                
                self._save_processed(msg_id)

        except Exception as e:
            logger.error(f"Error checking emails: {e}")

    def run_forever(self):
        logger.info("Gmail Cloud Watcher started in DRAFT-ONLY mode.")
        if not self.authenticate():
            logger.warning("Running without real Gmail API auth. Waiting for test triggers.")
            
        while True:
            try:
                self.check_new_emails()
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                logger.critical(f"Unhandled exception in Gmail Watcher loop: {e}")
                time.sleep(30) # Backoff

if __name__ == "__main__":
    watcher = GmailCloudWatcher()
    watcher.run_forever()
