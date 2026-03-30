"""
Gmail MCP Server — Digital FTE Gold Tier
Handles IMAP read + SMTP send using App Password credentials.
"""

import os
import imaplib
import smtplib
import email
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ── Load credentials ──────────────────────────────────────────────────────────
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

GMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS", "")
GMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")   # Must be a Google App Password

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_PATH = Path(__file__).parent.parent / "logs" / "gmail_server.log"

def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [GMAIL_SERVER] {msg}"
    print(line)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[LOG_ERROR] {e}")

# ── Helper: safe decode email header ─────────────────────────────────────────
def _decode_header(raw_header: str) -> str:
    try:
        parts = decode_header(raw_header or "")
        decoded = []
        for part, charset in parts:
            if isinstance(part, bytes):
                decoded.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(str(part))
        return " ".join(decoded)
    except Exception:
        return str(raw_header)

# ── Helper: extract body text from email message ──────────────────────────────
def _extract_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp  = str(part.get("Content-Disposition", ""))
            if ctype == "text/plain" and "attachment" not in disp:
                try:
                    body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="replace"
            )
        except Exception:
            body = ""
    return body.strip()[:2000]   # cap at 2 000 chars for summary purposes

# ── Public API ────────────────────────────────────────────────────────────────

def test_connection() -> dict:
    """
    Validates IMAP + SMTP credentials without touching emails.
    Returns {'imap': True/False, 'smtp': True/False, 'error': str|None}
    """
    result = {"imap": False, "smtp": False, "error": None}
    try:
        _log("Testing IMAP connection …")
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        imap.logout()
        result["imap"] = True
        _log("✅ IMAP connected")
    except Exception as e:
        result["error"] = f"IMAP: {e}"
        _log(f"❌ IMAP error: {e}")

    try:
        _log("Testing SMTP connection …")
        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        smtp.quit()
        result["smtp"] = True
        _log("✅ SMTP ready")
    except Exception as e:
        result["error"] = (result.get("error") or "") + f" | SMTP: {e}"
        _log(f"❌ SMTP error: {e}")

    return result


def fetch_unread_emails() -> list[dict]:
    """
    Fetches all unread emails from INBOX.
    Returns list of dicts:
      { uid, message_id, sender, reply_to, subject, date, body, snippet }
    """
    emails = []
    try:
        _log("Connecting to IMAP …")
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        imap.select("INBOX")

        _log("Searching for UNSEEN messages …")
        status, data = imap.search(None, "UNSEEN")
        if status != "OK" or not data[0]:
            _log("No unread messages found.")
            imap.logout()
            return []

        uids = data[0].split()
        _log(f"Found {len(uids)} unread message(s).")

        for uid in uids:
            try:
                status, msg_data = imap.fetch(uid, "(RFC822)")
                if status != "OK":
                    continue
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                sender    = _decode_header(msg.get("From", ""))
                reply_to  = _decode_header(msg.get("Reply-To", sender))
                subject   = _decode_header(msg.get("Subject", "(no subject)"))
                date      = msg.get("Date", "")
                msg_id    = msg.get("Message-ID", uid.decode())
                body      = _extract_body(msg)
                snippet   = body[:300].replace("\n", " ")

                emails.append({
                    "uid"        : uid.decode(),
                    "message_id" : msg_id,
                    "sender"     : sender,
                    "reply_to"   : reply_to,
                    "subject"    : subject,
                    "date"       : date,
                    "body"       : body,
                    "snippet"    : snippet,
                })
                _log(f"READ - UID={uid.decode()} | From={sender} | Subject={subject}")
            except Exception as e:
                _log(f"ERROR reading UID {uid}: {e}")

        imap.logout()
    except Exception as e:
        _log(f"IMAP_FATAL: {e}")

    return emails


def mark_as_read(uid: str) -> bool:
    """Mark a specific email UID as seen in Gmail."""
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        imap.select("INBOX")
        imap.store(uid, "+FLAGS", "\\Seen")
        imap.logout()
        _log(f"MARKED_READ - UID={uid}")
        return True
    except Exception as e:
        _log(f"MARK_READ_ERROR - UID={uid}: {e}")
        return False


def send_reply(to: str, subject: str, body: str, in_reply_to: str = "") -> bool:
    """
    Send an email reply via SMTP.
    to          : recipient address
    subject     : email subject (prefix 'Re: ' is added automatically if missing)
    body        : plain-text email body
    in_reply_to : original Message-ID for threading
    """
    if not subject.startswith("Re:"):
        subject = f"Re: {subject}"
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = to
        msg["Subject"] = subject
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"]  = in_reply_to
        msg.attach(MIMEText(body, "plain", "utf-8"))

        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, to, msg.as_string())
        smtp.quit()
        _log(f"EMAIL_SENT - To={to} | Subject={subject}")
        return True
    except Exception as e:
        _log(f"SEND_ERROR - To={to}: {e}")
        return False


def get_unread_count() -> int:
    """Returns count of unread emails in INBOX."""
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        imap.select("INBOX")
        status, data = imap.search(None, "UNSEEN")
        imap.logout()
        if status == "OK" and data[0]:
            return len(data[0].split())
        return 0
    except Exception as e:
        _log(f"COUNT_ERROR: {e}")
        return -1


if __name__ == "__main__":
    result = test_connection()
    print(result)
