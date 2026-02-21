import ai
from filters import is_safe
import ai
from filters import is_safe, sanitize_reply
import logging
import traceback


def run_tests():
    test_messages = [
        "Where are you?",
        "Did you eat?",
        "Why aren't you picking up?",
    ]

    print("Starting tests...")
    print("=" * 40)

    ok = True
    for msg in test_messages:
        try:
            raw = ai.generate_reply(msg)
            print(f"Mom: {msg}")
            assert isinstance(raw, str)
            assert len(raw) > 0
            assert is_safe(raw)
            safe = sanitize_reply(raw)
            print(f"Reply: {safe}")
            print("-" * 40)
        except AssertionError:
            ok = False
            logging.exception("Test failed for message: %s", msg)
        except Exception:
            ok = False
            traceback.print_exc()

    if not ok:
        raise SystemExit(1)

    print("Done.")


if __name__ == '__main__':
    run_tests()