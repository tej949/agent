BANNED_WORDS = ["lol", "omg", "CHILL", "wtf", "bruh", "lmao", "haha", "lmfao"]

SAFE_FALLBACK = "phone was on silent <3"

def is_from_mom(contact_name: str, mom_name: str) -> bool:
    """Check if the message is from mom only."""
    return contact_name.strip().lower() == mom_name.strip().lower()

def already_replied(last_message_sender: str) -> bool:
    """Prevent infinite reply loop — check if YOU sent the last message."""
    return last_message_sender.strip().lower() == "you"

def is_safe(reply: str) -> bool:
    """
    Validates AI reply before sending.
    Returns False if reply:
    - Contains a question (we don't want to start conversations)
    - Is too long (keep it brief like a real text)
    - Contains banned/casual words not appropriate for mom
    """
    if not reply or reply.strip() == "":
        return False

    if "?" in reply:
        return False

    if len(reply) > 200:
        return False

    if any(word in reply.lower() for word in [w.lower() for w in BANNED_WORDS]):
        return False

    return True

def sanitize_reply(reply: str) -> str:
    """
    If reply is unsafe, return the safe fallback message.
    Otherwise return the reply as-is.
    """
    if is_safe(reply):
        return reply.strip()
    return SAFE_FALLBACK

def is_duplicate(new_message: str, last_replied_message: str) -> bool:
    """Avoid replying to the same message twice."""
    if not last_replied_message:
        return False
    return new_message.strip() == last_replied_message.strip()