"""
WhatsApp Business Agent – Obsidian Logger
Writes conversation summaries as Markdown notes to /Inbox and /Needs_Action.
"""

import re
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
#  Vault Paths
# ─────────────────────────────────────────────

VAULT_ROOT      = Path(__file__).parent
INBOX_PATH      = VAULT_ROOT / "00_Inbox" / "WhatsApp"
NEEDS_ACTION_PATH = VAULT_ROOT / "Needs_Action"

INBOX_PATH.mkdir(parents=True, exist_ok=True)
NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _safe_filename(text: str) -> str:
    """Strip characters unsafe for filenames."""
    return re.sub(r'[\\/:*?"<>|]', "_", text)


def _build_note(
    sender_name:  str,
    category:     str,
    messages:     list[str],
    reply_sent:   str,
    hot:          bool,
    sensitive:    bool,
    approved:     bool,
    timestamp:    str,
) -> str:
    """Build Markdown content for the Obsidian note."""
    status_tags = []
    if hot:
        status_tags.append("#hot-lead")
    if sensitive:
        status_tags.append("#sensitive")
    if not approved:
        status_tags.append("#reply-skipped")

    tag_line = "  ".join(status_tags) if status_tags else "_none_"

    conversation_md = "\n".join(
        f"> **[Them]** {msg}" for msg in messages
    )

    note = f"""---
created: {timestamp}
contact: {sender_name}
category: {category}
status: unread
hot_lead: {str(hot).lower()}
sensitive: {str(sensitive).lower()}
reply_approved: {str(approved).lower()}
tags: [whatsapp, {category.lower().replace(' ', '-')}{''.join(', ' + t.lstrip('#') for t in status_tags)}]
---

# WhatsApp Chat – {sender_name}

| Field | Value |
|---|---|
| **Contact** | {sender_name} |
| **Category** | {category} |
| **Timestamp** | {timestamp} |
| **Hot Lead** | {"🔥 YES" if hot else "No"} |
| **Sensitive** | {"🔒 YES" if sensitive else "No"} |
| **Reply Sent** | {"✅ Yes" if approved else "⛔ Skipped"} |

---

## 💬 Conversation Summary

{conversation_md}

---

## 🤖 Auto-Reply Sent

```
{reply_sent if approved else "[Reply was NOT sent – human approval declined or skipped]"}
```

---

## 🏷️ Flags

{tag_line}

---
_Logged by WhatsApp Business Agent – Digital FTE_
"""
    return note


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def log_conversation(
    sender_name:  str,
    category:     str,
    messages:     list[str],
    reply_sent:   str,
    hot:          bool = False,
    sensitive:    bool = False,
    approved:     bool = True,
) -> dict:
    """
    Write a conversation summary note to /Inbox (and /Needs_Action if hot lead).

    Returns:
        dict with 'inbox_path' and optionally 'needs_action_path'
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str  = datetime.now().strftime("%Y-%m-%d")
    safe_name = _safe_filename(sender_name)

    note_content = _build_note(
        sender_name=sender_name,
        category=category,
        messages=messages,
        reply_sent=reply_sent,
        hot=hot,
        sensitive=sensitive,
        approved=approved,
        timestamp=timestamp,
    )

    result = {}

    # ── Write to Inbox ────────────────────────
    inbox_file = INBOX_PATH / f"{date_str}_{safe_name}.md"

    # Handle same-day duplicates by appending HHmmss
    if inbox_file.exists():
        ts_short  = datetime.now().strftime("%H%M%S")
        inbox_file = INBOX_PATH / f"{date_str}_{safe_name}_{ts_short}.md"

    inbox_file.write_text(note_content, encoding="utf-8")
    result["inbox_path"] = str(inbox_file)
    print(f"  📥 Logged → {inbox_file.name}")

    # ── Write to Needs_Action (hot leads) ─────
    if hot or sensitive:
        suffix = "_HOT" if hot else "_SENSITIVE"
        na_file = NEEDS_ACTION_PATH / f"{date_str}_{safe_name}{suffix}.md"

        if na_file.exists():
            ts_short = datetime.now().strftime("%H%M%S")
            na_file  = NEEDS_ACTION_PATH / f"{date_str}_{safe_name}{suffix}_{ts_short}.md"

        na_file.write_text(note_content, encoding="utf-8")
        result["needs_action_path"] = str(na_file)
        print(f"  🚨 Flagged → Needs_Action/{na_file.name}")

    return result


# ─────────────────────────────────────────────
#  Quick self-test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    paths = log_conversation(
        sender_name = "Test User",
        category    = "Lead",
        messages    = ["Hi, I want a demo of your services ASAP. Budget is approved."],
        reply_sent  = "Hello Test! We'd love to schedule a demo for you...",
        hot         = True,
        sensitive   = False,
        approved    = True,
    )
    print("\nCreated files:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
