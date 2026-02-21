import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()

YOUR_NAME = os.getenv("YOUR_NAME", "Teju")
LANGUAGE_STYLE = os.getenv("LANGUAGE_STYLE", "casual Telugu-English mix")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyD2rQPIwXIAP2ZXKHJxU1rQry4z3_jnlBo"

SAFE_FALLBACK = "phone was on silent <3"

SYSTEM_PROMPT = f"""You are {YOUR_NAME}, a 20-year-old engineering student replying to your mom on WhatsApp.
Short replies only, 1-2 sentences. Never ask questions back. Use Telugu words naturally. Stay calm and loving.

Mom: Where are you?
You: im in class

Mom: Did you eat?
You: yes i did

Mom: Why aren't you replying
You: sorry phone was on silent <3

Mom: Are you safe?
You: yes ma all good <3
"""

def generate_reply(message: str, contact: str = "") -> str:
    try:
        if not GOOGLE_API_KEY:
            logging.warning("No GOOGLE_API_KEY set; returning fallback reply")
            return SAFE_FALLBACK

        # Choose persona based on contact name
        contact_lower = (contact or "").lower()
        if "sujathamma" in contact_lower or "mom" in contact_lower:
            persona = f"""You are {YOUR_NAME} replying to your mom {contact} on WhatsApp.

CRITICAL: Reply ONLY in Roman script Tenglish (Telugu words written in English letters).
NEVER use Telugu script characters. NEVER use pure English.

Good examples:
- em chestunav ma
- tinanu don't worry
- sare le, call chesta
- class lo unna
- inka padukoledu, inkonchem time

Bad examples (never do this):
- ఏం చేస్తున్నావ్  ← Telugu script, FORBIDDEN
- I am in class  ← pure English, FORBIDDEN

Keep it 1-2 sentences. Never ask questions back. Stay calm and loving."""
        else:
            persona = (
                f"You are {YOUR_NAME}, replying to your FRIEND {contact}. "
                "Be casual and friendly. Short reply. "
                "Can use Telugu-English mix naturally."
            )

        full_prompt = persona + f"\n\nThey said: {message}\nYou:"

        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )

        text = response.text.strip() if response.text else ""
        return text if text else SAFE_FALLBACK

    except Exception as e:
        logging.exception("generate_reply error: %s", e)
        return SAFE_FALLBACK
