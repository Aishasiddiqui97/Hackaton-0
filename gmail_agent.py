"""
Gmail Autonomous Agent — Digital FTE Gold Tier
============================================================
Role   : Digital FTE — Gmail Manager
Loop   : Ralph Wiggum Stop Hook (run until inbox == 0 unread OR Ctrl+C)
Vault  : AI_Employee_Vault (Obsidian)

Usage:
    python gmail_agent.py               # Full autonomous run
    python gmail_agent.py --test-connection  # Validate credentials only
"""

from __future__ import annotations

import sys
import time
import signal
import hashlib
import textwrap
from datetime import datetime
from pathlib import Path

# ── Project root setup ────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).parent
VAULT_DIR   = ROOT_DIR / "AI_Employee_Vault"
INBOX_DIR   = VAULT_DIR / "Inbox"
APPROVAL_DIR = ROOT_DIR / "02_Pending_Approvals"   # existing folder at root
LOGS_DIR    = VAULT_DIR / "Logs"
AUDIT_DIR   = VAULT_DIR / "Audit"
PLANS_DIR   = VAULT_DIR / "Plans"

GMAIL_LOG   = LOGS_DIR / "Gmail_Log.md"

# ── MCP server + categorizer ──────────────────────────────────────────────────
sys.path.insert(0, str(ROOT_DIR / "mcp_servers"))
import gmail_server as gmx

sys.path.insert(0, str(ROOT_DIR))
import gmail_categorizer as cat

# ── Ensure directories exist ──────────────────────────────────────────────────
for d in [INBOX_DIR, APPROVAL_DIR, LOGS_DIR, AUDIT_DIR, PLANS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Agent identity ────────────────────────────────────────────────────────────
AGENT_NAME  = "Aisha Siddiqui"
AGENT_EMAIL = gmx.GMAIL_ADDRESS

# ── Globals ───────────────────────────────────────────────────────────────────
_running = True          # Ralph Wiggum stop flag
_session_stats: dict = {}   # per-run email stats


# ══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════════

def _log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        GMAIL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(GMAIL_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[LOG_WRITE_ERROR] {e}")


# ══════════════════════════════════════════════════════════════════════════════
# RALPH WIGGUM STOP HOOK
# ══════════════════════════════════════════════════════════════════════════════

def _on_sigint(sig, frame):
    global _running
    _log("🛑 STOP SIGNAL received — finishing current batch then exiting …", "WARN")
    _running = False


signal.signal(signal.SIGINT, _on_sigint)
signal.signal(signal.SIGTERM, _on_sigint)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — WRITE OBSIDIAN NOTE
# ══════════════════════════════════════════════════════════════════════════════

def _safe_uid(uid: str, subject: str) -> str:
    """Create a filesystem-safe short ID from uid + subject hash."""
    h = hashlib.md5(f"{uid}{subject}".encode()).hexdigest()[:8]
    return f"gmail-{h}"


def write_obsidian_note(em: dict, category: str) -> Path:
    """Save email details as a structured Obsidian .md note in Inbox."""
    note_id   = _safe_uid(em["uid"], em["subject"])
    note_path = INBOX_DIR / f"{note_id}.md"

    snippet = textwrap.fill(em["snippet"], width=100)
    needs_reply = cat.reply_required(category)

    content = f"""# 📧 Email — {em["subject"]}

| Field      | Value |
|------------|-------|
| **UID**      | `{em["uid"]}` |
| **From**     | {em["sender"]} |
| **Date**     | {em["date"]} |
| **Category** | `{category}` |
| **Reply Required** | {"✅ Yes" if needs_reply else "❌ No (Summary Only)"} |

## Summary
{snippet}

## Full Body
```
{em["body"][:1500]}
```

---
*Processed by Gmail Agent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    note_path.write_text(content, encoding="utf-8")
    _log(f"OBSIDIAN_NOTE_CREATED — {note_path.name} | Category={category}")
    return note_path


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — DRAFT REPLY + SAVE TO PENDING APPROVALS
# ══════════════════════════════════════════════════════════════════════════════

def create_approval_file(em: dict, category: str, draft_body: str) -> Path:
    """Write a pending-approval file for human review + approval."""
    note_id   = _safe_uid(em["uid"], em["subject"])
    appr_path = APPROVAL_DIR / f"reply-{note_id}.md"

    # Extract first name from sender for personalisation
    raw_name  = em["sender"].split("<")[0].strip().split()[0]

    content = f"""# 📨 Draft Reply — {em["subject"]}

> **INSTRUCTIONS FOR HUMAN REVIEW**
> - Change `APPROVAL_STATUS: PENDING` → `APPROVAL_STATUS: APPROVED` to send
> - Change `APPROVAL_STATUS: PENDING` → `APPROVAL_STATUS: REJECTED` to discard
> - You may edit the **Draft Body** below before approving

---

## Email Metadata
| Field | Value |
|-------|-------|
| **UID**       | `{em["uid"]}` |
| **To**        | {em["reply_to"]} |
| **Subject**   | Re: {em["subject"]} |
| **Category**  | `{category}` |
| **Timestamp** | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |

## APPROVAL_STATUS: PENDING

---

## Draft Body

{draft_body}

---
*Approval file created by Gmail Agent*
*Email Message-ID: {em["message_id"]}*
"""
    appr_path.write_text(content, encoding="utf-8")
    _log(f"APPROVAL_FILE_CREATED — {appr_path.name} | Waiting for human review …")
    return appr_path


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — POLL FOR APPROVAL (Human-in-the-Loop)
# ══════════════════════════════════════════════════════════════════════════════

POLL_INTERVAL_SEC  = 10       # check every 10 seconds
APPROVAL_TIMEOUT   = 300      # give up after 5 minutes (configurable)


def poll_for_approval(appr_path: Path) -> str:
    """
    Polls approval file every POLL_INTERVAL_SEC seconds.
    Returns: 'APPROVED' | 'REJECTED' | 'TIMEOUT'
    """
    _log(f"⏳ Waiting for approval: {appr_path.name}  (timeout {APPROVAL_TIMEOUT}s)")
    elapsed = 0

    while elapsed < APPROVAL_TIMEOUT:
        if not _running:
            return "REJECTED"
        try:
            text = appr_path.read_text(encoding="utf-8")
            if "APPROVAL_STATUS: APPROVED" in text:
                _log(f"✅ APPROVED — {appr_path.name}")
                return "APPROVED"
            if "APPROVAL_STATUS: REJECTED" in text:
                _log(f"🚫 REJECTED — {appr_path.name}")
                return "REJECTED"
        except Exception as e:
            _log(f"POLL_ERROR — {e}", "WARN")

        time.sleep(POLL_INTERVAL_SEC)
        elapsed += POLL_INTERVAL_SEC

    _log(f"⏰ TIMEOUT — No decision for {appr_path.name}. Treating as REJECTED.", "WARN")
    return "TIMEOUT"


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — SEND APPROVED REPLY
# ══════════════════════════════════════════════════════════════════════════════

def _extract_draft_from_approval_file(appr_path: Path) -> str:
    """Extract (possibly human-edited) draft body from approval file."""
    text = appr_path.read_text(encoding="utf-8")
    marker = "## Draft Body\n"
    sep    = "---\n*Approval file"
    start  = text.find(marker)
    end    = text.find(sep)
    if start == -1:
        return ""
    body_raw = text[start + len(marker): end if end != -1 else None]
    return body_raw.strip()


def send_approved_reply(em: dict, appr_path: Path) -> bool:
    """Read (possibly edited) draft from approval file and send."""
    draft = _extract_draft_from_approval_file(appr_path)
    if not draft:
        _log("SEND_SKIPPED — Empty draft body after extraction.", "WARN")
        return False

    success = gmx.send_reply(
        to         = em["reply_to"],
        subject    = em["subject"],
        body       = draft,
        in_reply_to= em["message_id"],
    )
    return success


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — ARCHIVE APPROVAL FILE
# ══════════════════════════════════════════════════════════════════════════════

def archive_approval_file(appr_path: Path, status: str):
    """Move approval file to AI_Employee_Vault/Done or mark as rejected."""
    done_dir = VAULT_DIR / "Done"
    done_dir.mkdir(parents=True, exist_ok=True)
    dest = done_dir / f"[{status}]-{appr_path.name}"
    try:
        appr_path.rename(dest)
        _log(f"ARCHIVED — {appr_path.name} → {dest.name}")
    except Exception as e:
        _log(f"ARCHIVE_ERROR — {e}", "WARN")


# ══════════════════════════════════════════════════════════════════════════════
# PROCESS ONE EMAIL
# ══════════════════════════════════════════════════════════════════════════════

def process_email(em: dict):
    """Full pipeline for a single email."""
    _log(f"\n{'='*60}")
    _log(f"PROCESSING — UID={em['uid']} | From={em['sender']} | Subject={em['subject']}")

    # 1. Categorise
    category = cat.categorize(em["subject"], em["body"], em["sender"])
    _log(f"CATEGORY — {category}")

    # Track stats
    _session_stats[category] = _session_stats.get(category, 0) + 1
    _session_stats["total"]  = _session_stats.get("total", 0) + 1

    # 2. Write Obsidian note
    write_obsidian_note(em, category)

    # 3. Draft reply if required
    if cat.reply_required(category):
        sender_name = em["sender"].split("<")[0].strip()
        draft_body  = cat.draft_reply(category, sender_name, AGENT_NAME)

        # 4. Create approval file
        appr_path   = create_approval_file(em, category, draft_body)

        # 5. Wait for human approval
        decision    = poll_for_approval(appr_path)

        # 6. Send or discard
        if decision == "APPROVED":
            sent = send_approved_reply(em, appr_path)
            if sent:
                _log(f"✉️  REPLY_SENT — To={em['reply_to']} | Subject=Re: {em['subject']}")
                _session_stats["sent"] = _session_stats.get("sent", 0) + 1
        else:
            _log(f"REPLY_SKIPPED — Decision={decision}")
            _session_stats["skipped"] = _session_stats.get("skipped", 0) + 1

        # Archive the approval file
        archive_approval_file(appr_path, decision)
    else:
        _log(f"SUMMARY_ONLY — Personal email. No reply drafted.")
        _session_stats["summary_only"] = _session_stats.get("summary_only", 0) + 1

    # 7. Mark as read in Gmail
    gmx.mark_as_read(em["uid"])
    _log(f"✅ EMAIL_COMPLETE — UID={em['uid']}")


# ══════════════════════════════════════════════════════════════════════════════
# AUDIT REPORT
# ══════════════════════════════════════════════════════════════════════════════

def write_audit_report():
    """Generate Daily Email Summary in AI_Employee_Vault/Audit/."""
    today     = datetime.now().strftime("%Y-%m-%d")
    now_ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rpt_path  = AUDIT_DIR / f"Email_Summary_{today}.md"

    total     = _session_stats.get("total", 0)
    sales     = _session_stats.get("Sales", 0)
    support   = _session_stats.get("Client Support", 0)
    personal  = _session_stats.get("Personal", 0)
    sent      = _session_stats.get("sent", 0)
    skipped   = _session_stats.get("skipped", 0)
    summary_only = _session_stats.get("summary_only", 0)

    report = f"""# 📊 Daily Email Summary — {today}

*Generated by Gmail Autonomous Agent at {now_ts}*

---

## 📬 Volume

| Metric | Count |
|--------|-------|
| Total Processed | {total} |
| Sales | {sales} |
| Client Support | {support} |
| Personal | {personal} |

## 📤 Actions

| Action | Count |
|--------|-------|
| Replies Sent | {sent} |
| Replies Skipped / Rejected | {skipped} |
| Summary Only (Personal) | {summary_only} |

---
## 🗂 Notes
- All email notes filed to `AI_Employee_Vault/Inbox/`
- All reply drafts routed through `02_Pending_Approvals/` for human approval
- Log file: `AI_Employee_Vault/Logs/Gmail_Log.md`
"""

    # Append if file already exists (multiple runs in same day)
    mode = "a" if rpt_path.exists() else "w"
    with open(rpt_path, mode, encoding="utf-8") as f:
        f.write(report if mode == "w" else f"\n---\n### Run at {now_ts}\n" + report)

    _log(f"📊 AUDIT_REPORT_WRITTEN — {rpt_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — RALPH WIGGUM LOOP
# ══════════════════════════════════════════════════════════════════════════════

def process_orphaned_approvals():
    """
    Scans APPROVAL_DIR for any files that have already been marked APPROVED
    but weren't sent/archived (perhaps due to a crash or closure).
    """
    _log("🔍 Scanning for orphaned approvals …")
    found_count = 0
    for f in APPROVAL_DIR.glob("reply-*.md"):
        try:
            text = f.read_text(encoding="utf-8")
            if "APPROVAL_STATUS: APPROVED" in text:
                # Extract metadata
                uid_match = re.search(r"\*\*UID\*\*\s*\|\s*`(.+?)`", text)
                to_match  = re.search(r"\*\*To\*\*\s*\|\s*([^|]+)", text)
                sub_match = re.search(r"\*\*Subject\*\*\s*\|\s*([^|]+)", text)
                msg_id_match = re.search(r"\*Email Message-ID: (.+)\*", text)

                if uid_match and to_match and sub_match:
                    _log(f"♻️ Recovering orphaned approval: {f.name}")
                    em_mock = {
                        "uid": uid_match.group(1).strip(),
                        "reply_to": to_match.group(1).strip(),
                        "subject": sub_match.group(1).replace("Re: ", "").strip(),
                        "message_id": msg_id_match.group(1).strip() if msg_id_match else ""
                    }
                    sent = send_approved_reply(em_mock, f)
                    if sent:
                        _session_stats["sent"] = _session_stats.get("sent", 0) + 1
                        archive_approval_file(f, "APPROVED")
                        found_count += 1
                else:
                    _log(f"⚠️ Skipped invalid approval file (missing metadata): {f.name}", "DEBUG")
        except Exception as e:
            _log(f"ORPHAN_PROCESS_ERROR — {f.name}: {e}", "WARN")
    
    if found_count > 0:
        _log(f"✅ Processed {found_count} orphaned approval(s).")
    else:
        _log("✨ No orphaned approvals found.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — CONTINUOUS LOOP
# ══════════════════════════════════════════════════════════════════════════════

import re

def main():
    global _running, _session_stats

    # ── CLI Flags ─────────────────────────────────────────────────────────────
    is_test = "--test-connection" in sys.argv
    is_continuous = "--continuous" in sys.argv

    if is_test:
        result = gmx.test_connection()
        print("\n=== Connection Test Results ===")
        print(f"  IMAP : {'✅ Connected' if result['imap'] else '❌ Failed'}")
        print(f"  SMTP : {'✅ Ready'     if result['smtp'] else '❌ Failed'}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        sys.exit(0 if (result["imap"] and result["smtp"]) else 1)

    # ── Header ────────────────────────────────────────────────────────────────
    _log("=" * 60)
    _log("🤖 GMAIL AUTONOMOUS AGENT STARTED")
    _log(f"   Agent  : {AGENT_NAME}")
    _log(f"   Account: {AGENT_EMAIL}")
    _log(f"   Vault  : {VAULT_DIR}")
    _log(f"   Mode   : {'Continuous Polling' if is_continuous else 'Ralph Wiggum Loop'}")
    _log("=" * 60)

    _session_stats   = {}
    loop_count       = 0
    processed_uids   = set()

    # Step 0: Startup Approval Recovery
    process_orphaned_approvals()

    try:
        while _running:
            loop_count += 1
            _log(f"\n🔄 LOOP #{loop_count} — Checking for unread emails …")

            # Fetch unread
            emails = gmx.fetch_unread_emails()
            new_emails = [e for e in emails if e["uid"] not in processed_uids]

            if not new_emails:
                if not is_continuous:
                    _log("📭 NO NEW UNREAD EMAILS — Stopping loop.")
                    break
                else:
                    _log("📭 NO NEW UNREAD EMAILS — Checking again in 60s …")
                    # Wait in smaller chunks to be responsive to Ctrl+C
                    for _ in range(12):
                        if not _running: break
                        time.sleep(5)
                    continue

            _log(f"📬 {len(new_emails)} new email(s) to process this pass.")

            for em in new_emails:
                if not _running:
                    break
                processed_uids.add(em["uid"])
                process_email(em)

            # Extra check for approvals that might have been marked in dashboard/files while processing
            # this prevents them sitting until the next loop check.
            process_orphaned_approvals()

            if is_continuous:
                _log(f"\n⏱  Waiting 30 s before next sweep …")
                for _ in range(6):
                    if not _running: break
                    time.sleep(5)
            else:
                _log("✅ Batch complete.")
                break

    except KeyboardInterrupt:
        _log("⌨️  KeyboardInterrupt caught — shutting down gracefully …", "WARN")
    except Exception as e:
        _log(f"💥 FATAL_ERROR — {e}", "ERROR")
        raise
    finally:
        _log("\n" + "=" * 60)
        _log("🏁 GMAIL AGENT STOPPED")
        _log(f"   Loops       : {loop_count}")
        _log(f"   Total emails: {_session_stats.get('total', 0)}")
        _log("=" * 60)
        write_audit_report()


if __name__ == "__main__":
    main()
