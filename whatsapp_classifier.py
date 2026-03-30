"""
WhatsApp Business Agent – Contact Classifier
Classifies senders as: Lead, Existing Client, Vendor, Unknown
Also detects "hot lead" signals for escalation to Needs_Action.
"""

import re

# ─────────────────────────────────────────────
#  Keyword Sets
# ─────────────────────────────────────────────

LEAD_KEYWORDS = [
    "interested", "demo", "pricing", "price", "quote", "inquiry",
    "enquiry", "package", "proposal", "trial", "free trial", "learn more",
    "how much", "cost", "looking for", "need", "help me", "can you", "want to",
    "services", "what do you offer", "tell me about", "information",
    "brochure", "catalogue", "catalog", "available", "when can", "schedule",
]

CLIENT_KEYWORDS = [
    "my order", "order#", "invoice", "payment done", "i paid", "delivery",
    "refund", "account", "my account", "subscription", "renewal", "support",
    "issue with", "problem with", "complaint", "ticket", "update me",
    "status", "follow up", "follow-up", "as discussed", "as per", "project",
    "login", "password", "access", "portal",
]

VENDOR_KEYWORDS = [
    "vendor", "supplier", "supply", "wholesale", "bulk", "distributor",
    "partnership", "collaborate", "commission", "reseller", "invoice from",
    "dispatch", "stock", "shipment", "consignment", "purchase order",
    "we offer", "our product", "our service", "business proposal",
    "rate card", "price list",
]

HOT_LEAD_KEYWORDS = [
    "urgent", "asap", "immediately", "today", "now", "this week",
    "demo request", "ready to buy", "want to purchase", "confirm order",
    "sign up", "let's proceed", "move forward", "finalize", "book",
    "meeting", "call me", "schedule a call", "whatsapp call",
    "how soon", "budget", "approved budget",
]

SENSITIVE_KEYWORDS = [
    "payment", "transfer", "bank account", "account number", "upi",
    "password", "otp", "secret", "confidential", "credit card", "debit card",
    "cvv", "pin", "iban", "wire transfer", "pay now", "send money",
]

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase + collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _score(messages: list[str], keywords: list[str]) -> int:
    """Count how many keyword hits appear across all messages."""
    combined = _normalise(" ".join(messages))
    return sum(1 for kw in keywords if kw in combined)


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def classify(sender_name: str, messages: list[str]) -> str:
    """
    Classify a WhatsApp contact based on sender name and conversation messages.

    Returns:
        One of: "Lead", "Existing Client", "Vendor", "Unknown"
    """
    name_lower = sender_name.lower()

    lead_score   = _score(messages, LEAD_KEYWORDS)
    client_score = _score(messages, CLIENT_KEYWORDS)
    vendor_score = _score(messages, VENDOR_KEYWORDS)

    # Name-based hints
    if any(w in name_lower for w in ["vendor", "supplier", "distributor", "supply", "wholesale"]):
        vendor_score += 3
    if any(w in name_lower for w in ["client", "customer", "member"]):
        client_score += 3

    scores = {
        "Lead":            lead_score,
        "Existing Client": client_score,
        "Vendor":          vendor_score,
    }

    best_category = max(scores, key=scores.get)
    best_score    = scores[best_category]

    if best_score == 0:
        return "Unknown"
    return best_category


def is_hot_lead(messages: list[str]) -> bool:
    """Return True if conversation contains hot-lead urgency signals."""
    return _score(messages, HOT_LEAD_KEYWORDS) >= 1


def is_sensitive(messages: list[str]) -> bool:
    """Return True if conversation contains payment / sensitive data keywords."""
    return _score(messages, SENSITIVE_KEYWORDS) >= 1


# ─────────────────────────────────────────────
#  Quick self-test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("New Person",        ["I am interested in your services, can I get a demo?"],),
        ("Client Ahmed",      ["My order is delayed, please update me on delivery status."],),
        ("ABC Supplier Ltd",  ["We supply wholesale stock, here is our price list."],),
        ("Random Guy",        ["Hi there!"],),
    ]
    for sender, msgs in tests:
        cat  = classify(sender, msgs)
        hot  = is_hot_lead(msgs)
        sens = is_sensitive(msgs)
        print(f"  [{cat}{'🔥' if hot else ''}{'🔒' if sens else ''}]  {sender!r}  →  {msgs[0][:60]}")
