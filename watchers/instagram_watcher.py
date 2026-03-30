#!/usr/bin/env python3
"""
Instagram Watcher - Gold Tier
Continuously monitors Instagram comments and DMs for business inquiries
Creates Needs_Action files for human review
"""

import json
import time
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Set, Dict, Any
import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Configuration
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
CHECK_INTERVAL = 300  # 5 minutes

# Vault paths
VAULT_ROOT = Path(__file__).parent / "AI_Employee_Vault"
NEEDS_ACTION_DIR = VAULT_ROOT / "Needs_Action"
STATE_DIR = VAULT_ROOT / ".state"
SIGNALS_DIR = VAULT_ROOT / "Signals"
LOGS_DIR = VAULT_ROOT / "Logs"
COMPANY_HANDBOOK = VAULT_ROOT / "Company_Handbook.md"

# Create directories
for dir_path in [NEEDS_ACTION_DIR, STATE_DIR, SIGNALS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# State file
STATE_FILE = STATE_DIR / "instagram_processed.json"

# Logging
LOG_PATH = LOGS_DIR / "instagram_watcher.log"
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [INSTAGRAM_WATCHER] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Business keywords to flag
BUSINESS_KEYWORDS = [
    'price', 'cost', 'buy', 'order', 'available',
    'interested', 'contact', 'how much', 'dm', 'link',
    'purchase', 'shipping', 'delivery', 'payment',
    'book', 'reserve', 'appointment', 'quote'
]


class InstagramWatcher:
    """Monitors Instagram for comments and DMs requiring attention."""

    def __init__(self):
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        self.account_id = INSTAGRAM_ACCOUNT_ID
        self.base_url = "https://graph.facebook.com/v21.0"
        self.processed_ids = self._load_state()
        self.backoff_time = 60  # Start with 1 minute backoff
        self.max_backoff = 480  # Max 8 minutes

        if not self.access_token or not self.account_id:
            logger.error("Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID")
            sys.exit(1)

    def _load_state(self) -> Dict[str, Set[str]]:
        """Load processed IDs from state file."""
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding='utf-8'))
                return {
                    'comments': set(data.get('comments', [])),
                    'dms': set(data.get('dms', []))
                }
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")

        return {'comments': set(), 'dms': set()}

    def _save_state(self):
        """Save processed IDs to state file."""
        try:
            data = {
                'comments': list(self.processed_ids['comments']),
                'dms': list(self.processed_ids['dms']),
                'last_updated': datetime.now().isoformat()
            }
            STATE_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception as e:
            logger.error(f"Could not save state: {e}")

    def _make_request(self, method: str, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make API request with error handling."""
        params = params or {}
        params['access_token'] = self.access_token

        url = f"{self.base_url}/{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=30)
            else:
                response = requests.post(url, params=params, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_data = response.json() if response.text else {}
            error_code = error_data.get('error', {}).get('code')

            if error_code == 190:
                logger.error("Access token expired or invalid")
                self._create_auth_signal()
                raise

            logger.error(f"HTTP Error {response.status_code}: {e}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise

    def _create_auth_signal(self):
        """Create signal file when authentication fails."""
        signal_file = SIGNALS_DIR / "INSTAGRAM_AUTH_NEEDED.md"
        content = f"""---
type: signal
platform: instagram
severity: critical
created: {datetime.now().isoformat()}
---

# Instagram Authentication Required

Your Instagram access token has expired or is invalid.

## Action Required

1. Run: `python refresh_instagram_token.py`
2. Follow the prompts to generate a new 60-day token
3. Update your .env file with the new token
4. Restart the Instagram watcher: `pm2 restart instagram_watcher`

## Current Status
- Token expired: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Account ID: {self.account_id}
- Watcher paused until token is refreshed
"""
        signal_file.write_text(content, encoding='utf-8')
        logger.info(f"Created auth signal: {signal_file}")

    def _generate_suggested_reply(self, comment_text: str, username: str) -> str:
        """Generate suggested reply based on comment content."""
        comment_lower = comment_text.lower()

        # Read company info if available
        company_name = "our team"
        if COMPANY_HANDBOOK.exists():
            try:
                handbook = COMPANY_HANDBOOK.read_text(encoding='utf-8')
                # Try to extract company name
                for line in handbook.split('\n'):
                    if 'company' in line.lower() or 'business' in line.lower():
                        company_name = line.split(':')[-1].strip() if ':' in line else company_name
                        break
            except:
                pass

        # Generate contextual reply
        if any(word in comment_lower for word in ['price', 'cost', 'how much']):
            return f"Hi @{username}! Thanks for your interest. I'll send you pricing details via DM. 😊"

        elif any(word in comment_lower for word in ['available', 'stock', 'order']):
            return f"Hi @{username}! Yes, this is available. Let me DM you the details!"

        elif any(word in comment_lower for word in ['interested', 'want', 'need']):
            return f"Hi @{username}! Great to hear! I'll reach out via DM with more information. 🙌"

        elif any(word in comment_lower for word in ['contact', 'dm', 'message']):
            return f"Hi @{username}! Absolutely! Sending you a DM now. 📩"

        else:
            return f"Hi @{username}! Thanks for reaching out! Let me get back to you with details. 😊"

    def _create_comment_action_file(self, comment: Dict[str, Any]):
        """Create Needs_Action file for a comment."""
        comment_id = comment['comment_id']
        username = comment['username']
        text = comment['text']
        post_caption = comment['post_caption']
        keywords = comment['keywords_matched']

        # Generate filename
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_'))
        filename = f"INSTAGRAM_comment_{safe_username}_{comment_id[:8]}.md"
        filepath = NEEDS_ACTION_DIR / filename

        # Generate suggested reply
        suggested_reply = self._generate_suggested_reply(text, username)

        content = f"""---
type: instagram_comment
from: {username}
post_id: {comment['post_id']}
comment_id: {comment_id}
received: {comment['timestamp']}
keyword_matched: {', '.join(keywords)}
status: pending
---

# Instagram Comment from @{username}

## Comment Text
{text}

## Post Caption
{post_caption}

## Suggested Reply
{suggested_reply}

## To Approve Reply
1. Review the suggested reply above
2. Edit if needed
3. Run: `python approve_instagram.py --approve {filename}`

Or move this file to /Vault/Approved/ to approve as-is.

## To Reject
Run: `python approve_instagram.py --reject {filename}`
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created action file: {filename}")

    def _create_dm_action_file(self, conversation: Dict[str, Any]):
        """Create Needs_Action file for a DM conversation."""
        conv_id = conversation['id']
        timestamp = conversation.get('updated_time', datetime.now().isoformat())

        filename = f"INSTAGRAM_dm_{conv_id[:8]}.md"
        filepath = NEEDS_ACTION_DIR / filename

        content = f"""---
type: instagram_dm
conversation_id: {conv_id}
received: {timestamp}
status: pending
---

# Instagram DM Conversation

## Conversation ID
{conv_id}

## Last Updated
{timestamp}

## Action Required
Review this conversation in Instagram and respond appropriately.

Note: Instagram DM API has limited functionality. You may need to respond directly in the Instagram app.

## To Mark as Done
Move this file to /Vault/Done/
"""

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created DM action file: {filename}")

    def check_comments(self):
        """Check for new comments with business keywords."""
        try:
            logger.info("Checking for new comments...")

            # Get recent media
            media_endpoint = f"{self.account_id}/media"
            media_params = {"fields": "id,caption", "limit": 5}
            media_data = self._make_request('GET', media_endpoint, params=media_params)

            new_comments_count = 0

            for media in media_data.get('data', []):
                media_id = media['id']
                media_caption = media.get('caption', '')[:100]

                # Get comments for this media
                comments_endpoint = f"{media_id}/comments"
                comments_params = {"fields": "id,username,text,timestamp", "limit": 20}

                try:
                    comments_data = self._make_request('GET', comments_endpoint, params=comments_params)

                    for comment in comments_data.get('data', []):
                        comment_id = comment['id']

                        # Skip if already processed
                        if comment_id in self.processed_ids['comments']:
                            continue

                        comment_text = comment.get('text', '').lower()

                        # Check for business keywords
                        matched_keywords = [kw for kw in BUSINESS_KEYWORDS if kw in comment_text]

                        if matched_keywords:
                            # Create action file
                            comment_info = {
                                'comment_id': comment_id,
                                'username': comment.get('username'),
                                'text': comment.get('text'),
                                'timestamp': comment.get('timestamp'),
                                'post_id': media_id,
                                'post_caption': media_caption,
                                'keywords_matched': matched_keywords
                            }

                            self._create_comment_action_file(comment_info)
                            new_comments_count += 1

                        # Mark as processed
                        self.processed_ids['comments'].add(comment_id)

                except Exception as e:
                    logger.warning(f"Could not get comments for {media_id}: {e}")

            if new_comments_count > 0:
                logger.info(f"Found {new_comments_count} new comments needing attention")
            else:
                logger.info("No new comments requiring attention")

            # Reset backoff on success
            self.backoff_time = 60

        except Exception as e:
            logger.error(f"Error checking comments: {e}")
            raise

    def check_dms(self):
        """Check for new DM conversations."""
        try:
            logger.info("Checking for new DMs...")

            conversations_endpoint = f"{self.account_id}/conversations"
            conversations_params = {"fields": "id,updated_time,message_count"}

            try:
                result = self._make_request('GET', conversations_endpoint, params=conversations_params)

                new_dms_count = 0

                for conversation in result.get('data', []):
                    conv_id = conversation['id']

                    # Skip if already processed
                    if conv_id in self.processed_ids['dms']:
                        continue

                    # Create action file
                    self._create_dm_action_file(conversation)
                    new_dms_count += 1

                    # Mark as processed
                    self.processed_ids['dms'].add(conv_id)

                if new_dms_count > 0:
                    logger.info(f"Found {new_dms_count} new DM conversations")
                else:
                    logger.info("No new DM conversations")

            except Exception as e:
                if "permission" in str(e).lower():
                    logger.warning("Instagram Messaging permission not enabled - skipping DM check")
                else:
                    raise

        except Exception as e:
            logger.error(f"Error checking DMs: {e}")
            # Don't raise - DM check is optional

    def run(self):
        """Main watcher loop."""
        logger.info("Instagram Watcher started")
        logger.info(f"Checking every {CHECK_INTERVAL} seconds")

        while True:
            try:
                # Check comments
                self.check_comments()

                # Check DMs
                self.check_dms()

                # Save state
                self._save_state()

                # Wait for next check
                logger.info(f"Sleeping for {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                logger.info("Watcher stopped by user")
                self._save_state()
                break

            except Exception as e:
                error_str = str(e)

                # Check if auth error
                if "190" in error_str or "token" in error_str.lower():
                    logger.error("Authentication error - pausing watcher")
                    logger.info("Fix authentication and restart watcher")
                    break

                # Exponential backoff for other errors
                logger.error(f"Error in watcher loop: {e}")
                logger.info(f"Backing off for {self.backoff_time} seconds...")
                time.sleep(self.backoff_time)

                # Increase backoff time
                self.backoff_time = min(self.backoff_time * 2, self.max_backoff)


def main():
    """Entry point."""
    watcher = InstagramWatcher()
    watcher.run()


if __name__ == "__main__":
    main()
