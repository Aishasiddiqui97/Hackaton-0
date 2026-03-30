"""
Gmail Categorizer — Digital FTE Gold Tier
Classifies emails into: Sales | Client Support | Personal
"""

from __future__ import annotations

# ── Keyword Rules ─────────────────────────────────────────────────────────────
CATEGORY_RULES: dict[str, list[str]] = {
    "Sales": [
        "quote", "quotation", "invoice", "purchase", "pricing", "price list",
        "proposal", "order", "buy", "payment", "billing", "subscription",
        "renewal", "contract", "deal", "offer", "discount", "product demo",
        "interested in", "sales", "revenue", "budget", "cost",
    ],
    "Client Support": [
        "issue", "bug", "error", "help", "support", "problem", "ticket",
        "urgent", "fix", "broken", "not working", "crash", "failure",
        "complain", "complaint", "refund", "escalation", "deadline",
        "question", "inquiry", "assistance", "cannot", "can't", "won't",
        "unable to", "feedback", "review", "rating",
    ],
    # Personal is the fallback — matched last
    "Personal": [],
}

REPLY_REQUIRED: dict[str, bool] = {
    "Sales": True,
    "Client Support": True,
    "Personal": False,   # Summarise only — no auto-draft for personal
}

# ── Draft Templates ───────────────────────────────────────────────────────────
DRAFT_TEMPLATES: dict[str, str] = {
    "Sales": (
        "Thank you for your interest!\n\n"
        "I've received your message and will review your enquiry shortly. "
        "Our team will get back to you with a detailed response within 1–2 business days.\n\n"
        "Best regards,\n{name}"
    ),
    "Client Support": (
        "Thank you for reaching out.\n\n"
        "I've noted the issue you've described and have escalated it to our support team. "
        "We will investigate and follow up with a resolution as quickly as possible. "
        "Your patience is greatly appreciated.\n\n"
        "Best regards,\n{name}"
    ),
    "Personal": "",   # No auto-draft
}


def categorize(subject: str, body: str, sender: str = "") -> str:
    """
    Returns category string: 'Sales' | 'Client Support' | 'Personal'
    Matches against subject + first 500 chars of body.
    """
    text = f"{subject} {body[:500]}".lower()

    for category, keywords in CATEGORY_RULES.items():
        if category == "Personal":
            continue   # Skip — it's the fallback
        for kw in keywords:
            if kw in text:
                return category

    return "Personal"


def reply_required(category: str) -> bool:
    """Returns True if the category warrants an auto-drafted reply."""
    return REPLY_REQUIRED.get(category, False)


def draft_reply(category: str, sender_name: str, agent_name: str = "Aisha Siddiqui") -> str:
    """
    Returns a draft reply string for the given category.
    Returns empty string for Personal or unknown categories.
    """
    template = DRAFT_TEMPLATES.get(category, "")
    if not template:
        return ""
    return template.format(name=agent_name)


# ── Self-test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("Quotation Request for 50 units", "Could you please send me a price list?", ""),
        ("URGENT: App is down", "Our production system is crashing, need immediate help!", ""),
        ("Lunch tomorrow?", "Hey! Are you free for lunch tomorrow?", ""),
        ("Invoice #1042 overdue", "Your payment for invoice #1042 is now overdue.", ""),
        ("Support Ticket #8821", "Unable to login, getting an error 500.", ""),
    ]

    print("\n=== Gmail Categorizer Self-Test ===\n")
    for subject, body, sender in tests:
        cat   = categorize(subject, body, sender)
        reply = reply_required(cat)
        draft = draft_reply(cat, "Test User")
        print(f"Subject : {subject}")
        print(f"Category: {cat}")
        print(f"Reply?  : {reply}")
        if draft:
            print(f"Draft   : {draft[:80]}…")
        print("-" * 60)
