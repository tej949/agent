"""WhatsApp Mom Auto-Reply Agent
Only replies to mom, uses Gemini for short calm replies.
"""

import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

CONTACTS = [
    os.getenv("MOM_CONTACT_NAME", "Sujathamma"),
    os.getenv("FRIEND_CONTACT_NAME", "Sharmishta"),
]
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "15"))

from whatsapp import get_driver, load_whatsapp, open_chat, get_last_message, send_message
from ai import generate_reply
from filters import already_replied, is_duplicate, sanitize_reply, mark_replied, is_safe

logging.basicConfig(level=logging.INFO)


def main():
    driver = None
    try:
        driver = get_driver()
        ok = load_whatsapp(driver)
        if not ok:
            logging.error("WhatsApp failed to load")
            return

        logging.info("Watching contacts: %s", CONTACTS)

        while True:
            for contact in CONTACTS:
                try:
                    if not open_chat(driver, contact):
                        continue

                    msg = get_last_message(driver)
                    if not msg:
                        continue

                    msg_id, is_from_me, text = msg

                    if not text or is_from_me:
                        continue

                    if already_replied(msg_id):
                        continue

                    if is_duplicate(text):
                        logging.info("Duplicate detected; marking replied for %s", contact)
                        mark_replied(msg_id, text)
                        continue

                    reply = generate_reply(text, contact=contact)
                    reply = sanitize_reply(reply)

                    if not is_safe(reply):
                        logging.info("Reply not safe; using fallback for %s", contact)
                        reply = "phone was on silent <3"

                    sent = send_message(driver, reply)
                    if sent:
                        mark_replied(msg_id, text)

                        logging.info("[Agent → %s] %s", contact, reply)

                except Exception as e:
                    logging.exception("Error handling contact %s: %s", contact, e)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Shutting down")
    except Exception as e:
        logging.exception("main loop error: %s", e)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()