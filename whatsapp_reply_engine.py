"""
WhatsApp Business Agent – Reply Engine
Generates professional, business-tone replies based on contact classification.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.startswith("AIza"):
        client = genai.Client(api_key=api_key)
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False

# ─────────────────────────────────────────────
#  Reply Templates  (slot: {name}, {topic})
# ─────────────────────────────────────────────

TEMPLATES = {
    "Lead": [
        "Hi! Of course 😊 Do you need help with an AI-powered website, chatbot, or automation system?",
        "Hello! I'd love to help you build smart business tools. What kind of automation are you looking for?",
    ],
    "Existing Client": [
        "Hi! Thanks for reaching out again. Let me check on your request and update you shortly.",
        "Hello! We are looking into your query right now. Our team will assist you soon.",
    ],
    "Vendor": [
        "Hi! We've received your message. Our team will review your proposal and get back to you.",
        "Thank you! We've noted your details and will be in touch if it matches our needs.",
    ],
    "Unknown": [
        "We help businesses build AI-powered websites, smart chatbots, and automation systems that save time and improve customer experience.",
        "Hi! How can I help you today?",
    ],
    "Greeting": [
        "Hello! 👋 How can I help you today?",
        "Hi there! 😊 How can we assist you with our AI solutions?",
    ],
    "Pricing": [
        "Thanks for asking! Pricing depends on the project requirements. Our team can share the full details with you shortly.",
    ],
    "Unreadable": [
        "Hi! I noticed your message but couldn’t read it clearly. Could you please clarify or resend it as text?",
    ]
}

SENSITIVE_PAUSE_MESSAGE = (
    "\n⚠️  [HUMAN APPROVAL REQUIRED]\n"
    "Conversation with {name} contains SENSITIVE / PAYMENT-related content.\n"
    "Auto-reply has been PAUSED.\n"
    "Proposed reply:\n"
    "─────────────────────────────────\n"
    "{reply}\n"
    "─────────────────────────────────\n"
    "Type 'yes' to approve and send, or 'no' to skip: "
)


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def _extract_topic(messages: list[str]) -> str:
    """Pull the most relevant topic noun from the last message (simple heuristic)."""
    if not messages:
        return "your inquiry"
    last = messages[-1].strip()
    # Truncate to ≤50 chars for display
    return last[:50] + ("…" if len(last) > 50 else "")


def _pick_template(category: str, seed: int = 0) -> str:
    """Pick template for category; cycle through alternatives using seed."""
    options = TEMPLATES.get(category, TEMPLATES["Unknown"])
    return options[seed % len(options)]


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

def generate_reply(
    category: str,
    sender_name: str,
    messages: list[str],
    template_seed: int = 0,
) -> str:
    """
    Generate an intelligent, concise WhatsApp reply. Uses Gemini AI if available.
    """
    last_msg = messages[-1].strip() if messages else ""
    
    # Rule 8 Edge Cases: Unreadable or Media
    if not last_msg or "image omitted" in last_msg.lower() or "sticker omitted" in last_msg.lower() or "video omitted" in last_msg.lower():
        return TEMPLATES["Unreadable"][0]
        
    # --- Try Gemini AI First ---
    if GEMINI_AVAILABLE:
        try:
            prompt = f"""
            You are an Autonomous WhatsApp Assistant for NIC Karachi AI/Business services.
            I will provide you with a recent chat message from a user.
            Your task is to generate a professional, concise, and helpful reply.

            Customer Name: {sender_name}
            Customer Category: {category}
            Last Message: "{last_msg}"

            GUIDELINES:
            1. Introduce yourself as an AI assistant if they say 'Hi' or 'Hello'.
            2. Match the language of the customer (Urdu/English/Hinglish).
            3. If they ask about the Hackathon or AI courses, provide encouraging details and mention NIC Karachi's support.
            4. Keep the tone friendly but professional.
            5. Keep the reply under 2 sentences. No placeholders like [Name].
            6. If they ask about pricing, mention custom quotes are based on specific needs.

            Generate the professional reply:
            """
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"⚠️ Gemini API Error: {e}. Falling back to templates.")

    # --- Fallback to Templates ---
    last_msg_lower = last_msg.lower()
    
    # Rule: Greetings
    if last_msg_lower in ["hi", "hello", "hey", "good morning", "good evening", "hi there", "salam", "assalam o alaikum"]:
        return _pick_template("Greeting", template_seed)
        
    # Rule: Pricing queries
    if any(word in last_msg_lower for word in ["price", "cost", "pricing", "charges", "fee", "paisa"]):
        return TEMPLATES["Pricing"][0]
        
    # Rule: Services / Generic inquiry
    if any(word in last_msg_lower for word in ["service", "services", "offer", "provide", "what do you do"]):
        return TEMPLATES["Unknown"][0]
        
    # Standard fallback
    return _pick_template(category, template_seed)


def request_human_approval(sender_name: str, reply: str) -> bool:
    """
    Block and ask the human operator whether to send a sensitive reply.

    Returns True if approved, False if skipped.
    """
    prompt = SENSITIVE_PAUSE_MESSAGE.format(name=sender_name, reply=reply)
    try:
        answer = input(prompt).strip().lower()
        return answer in ("yes", "y", "approve", "send")
    except (EOFError, KeyboardInterrupt):
        print("\n[Approval skipped – no input received.]")
        return False


# ─────────────────────────────────────────────
#  Quick self-test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    categories = ["Lead", "Existing Client", "Vendor", "Unknown"]
    messages   = ["I need a price list for your services ASAP."]

    for i, cat in enumerate(categories):
        print(f"\n=== {cat} ===")
        reply = generate_reply(cat, "Sara Khan", messages, template_seed=i)
        print(reply)
