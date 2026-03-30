"""
Intelligent Message Management Agent [AUTONOMOUS]
Processes incoming messages automatically and generates drafts for approval.
Runs in a continuous loop to provide real-time drafting.
"""

import os
import re
import yaml
import time
import argparse
from pathlib import Path
from datetime import datetime
from whatsapp_classifier import classify, is_hot_lead, is_sensitive
from whatsapp_reply_engine import generate_reply

# Paths
VAULT_ROOT = Path(__file__).parent
INBOX_PATH = VAULT_ROOT / "00_Inbox" / "WhatsApp"
NEEDS_ACTION_PATH = VAULT_ROOT / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_ROOT / "02_Pending_Approvals" / "WhatsApp"

# Ensure directories exist
INBOX_PATH.mkdir(parents=True, exist_ok=True)
NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
PENDING_APPROVAL_PATH.mkdir(parents=True, exist_ok=True)

def parse_frontmatter(content):
    """Simple frontmatter parser."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        yaml_block = match.group(1)
        body = match.group(2)
        try:
            metadata = yaml.safe_load(yaml_block)
            return metadata, body
        except yaml.YAMLError:
            return {}, body
    return {}, content

def build_frontmatter(metadata):
    """Simple frontmatter builder."""
    yaml_text = yaml.dump(metadata, sort_keys=False).strip()
    return f"---\n{yaml_text}\n---\n"

def process_messages():
    """Scan Inbox for unread/read messages and process them."""
    files = list(INBOX_PATH.glob("*.md"))
    processed_count = 0
    
    for file_path in files:
        # Ignore task.md
        if file_path.name == "task.md":
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        metadata, body = parse_frontmatter(content)
        status = metadata.get('status', '').lower()
        
        # Rule: Process messages with status = "unread" or "read"
        # We skip "Need Action" because they are already processed
        if status in ['unread', 'read']:
            sender = metadata.get('contact', 'Unknown')
            category = metadata.get('category', 'Unknown')
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-processing message from: {sender} (Status: {status})")
            
            # Step 1: Update status to "Need Action" and Tag it
            metadata['status'] = 'Need Action'
            if 'tags' not in metadata:
                metadata['tags'] = []
            
            # Ensure "need-action" tag is present
            if 'need-action' not in metadata['tags']:
                metadata['tags'].append('need-action')
            
            # Update the original file
            new_content = build_frontmatter(metadata) + body
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Copy to Needs_Action for visibility
            na_file = NEEDS_ACTION_PATH / file_path.name
            with open(na_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Step 2: Generate output and save to Pending Approval
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            original_id = file_path.stem
            
            # Extract message from body (heuristic)
            msg_match = re.search(r'> \*\*\[Them\]\*\* (.*)', body)
            original_msg = msg_match.group(1) if msg_match else "No message found"
            
            # Generate draft reply
            draft_reply = generate_reply(category, sender, [original_msg])
            
            approval_note = f"""# Pending Approval: {sender}
Reference ID: {original_id}
Original Sender: {sender}
Timestamp: {timestamp}

## Original Message
> {original_msg}

## Generated Draft Response
```
{draft_reply}
```

---
**Review Instructions:**
- To approve: Move this file to the 'Approved' state.
- To edit: Modify the draft above.
"""
            approval_file = PENDING_APPROVAL_PATH / f"Approval_{original_id}.md"
            approval_file.write_text(approval_note, encoding='utf-8')
            
            print(f"  ✅ Tagged as Need Action and created draft: {approval_file.name}")
            processed_count += 1
            
    return processed_count

def main():
    parser = argparse.ArgumentParser(description="Intelligent Message Manager [AUTONOMOUS]")
    parser.add_argument("--loop", action="store_true", help="Run in a continuous loop")
    parser.add_argument("--interval", type=int, default=30, help="Interval in seconds (default: 30)")
    args = parser.parse_args()

    print(f"Intelligent Message Manager - Autonomous Mode Started")
    print(f"Inbox: {INBOX_PATH}")
    print(f"Loop: {args.loop} | Interval: {args.interval}s")
    print("-" * 50)

    try:
        while True:
            processed = process_messages()
            if processed > 0:
                print(f"Processed {processed} message(s).")
            
            if not args.loop:
                break
                
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nManager stopped by user.")

if __name__ == "__main__":
    main()
