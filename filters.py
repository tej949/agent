import os
import re
import json
import hashlib
import logging
import traceback
from typing import Optional

BAN_LIST = {"lol", "omg", "wtf", "bruh", "lmao", "haha", "lmfao"}
SAFE_FALLBACK = "phone was on silent <3"
REPLIED_DB = os.path.join(os.path.dirname(__file__), "replied.json")


def _load_db() -> dict:
    try:
        if not os.path.exists(REPLIED_DB):
            return {"ids": {}, "texts": {}}
        with open(REPLIED_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logging.debug("Failed to load replied DB: %s", traceback.format_exc())
        return {"ids": {}, "texts": {}}


def _save_db(db: dict):
    try:
        with open(REPLIED_DB, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception:
        logging.exception("Failed to save replied DB: %s", traceback.format_exc())


def _normalize(text: str) -> str:
    try:
        return re.sub(r"\s+", " ", text.strip().lower())
    except Exception:
        return text


def is_safe(reply: str) -> bool:
    try:
        if not isinstance(reply, str) or not reply.strip():
            return False
        if "?" in reply:
            return False
        if len(reply) > 200:
            return False
        low = reply.lower()
        for banned in BAN_LIST:
            if banned in low:
                return False
        return True
    except Exception:
        logging.debug("is_safe error: %s", traceback.format_exc())
        return False


def sanitize_reply(reply: Optional[str]) -> str:
    try:
        if not reply:
            return SAFE_FALLBACK
        r = re.sub(r"\s+", " ", reply.strip())
        # remove trailing question marks if any
        if r.endswith("?"):
            r = r.rstrip("?")
            r = r.strip()
        if not is_safe(r):
            return SAFE_FALLBACK
        return r
    except Exception:
        logging.exception("sanitize_reply error: %s", traceback.format_exc())
        return SAFE_FALLBACK


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def already_replied(message_id: str) -> bool:
    try:
        db = _load_db()
        return message_id in db.get("ids", {})
    except Exception:
        logging.debug("already_replied error: %s", traceback.format_exc())
        return False


def mark_replied(message_id: str, message_text: str):
    try:
        db = _load_db()
        db.setdefault("ids", {})[message_id] = True
        db.setdefault("texts", {})[_hash_text(_normalize(message_text))] = True
        _save_db(db)
    except Exception:
        logging.exception("mark_replied error: %s", traceback.format_exc())


def is_duplicate(message_text: str) -> bool:
    try:
        db = _load_db()
        h = _hash_text(_normalize(message_text))
        return h in db.get("texts", {})
    except Exception:
        logging.debug("is_duplicate error: %s", traceback.format_exc())
        return False
