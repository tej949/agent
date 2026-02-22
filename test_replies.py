import ai
from filters import is_safe
import logging

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
        raw = generate_reply(msg)
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
    except Exception as e:
        print(f"ERROR on message '{msg}':")
        traceback.print_exc()
        print("-" * 40)

if not ok:
    raise SystemExit(1)

print("Done.")

test_messages = [
    "Where are you?",
    "Did you eat?",
    "Why aren't you picking up?",
]

print("Starting tests...")
print("=" * 40)

for msg in test_messages:
    try:
        raw = generate_reply(msg)
        safe = sanitize_reply(raw)
        print(f"Mom: {msg}")
        print(f"Reply: {safe}")
        print("-" * 40)
    except Exception as e:
        print(f"ERROR on message '{msg}':")
        traceback.print_exc()
        print("-" * 40)

print("Done.")