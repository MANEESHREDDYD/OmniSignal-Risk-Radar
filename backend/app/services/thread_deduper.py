from __future__ import annotations

import re
from difflib import SequenceMatcher


def normalize_subject(value: str | None) -> str:
    value = re.sub(r"^(re|fw|fwd):\s*", "", value or "", flags=re.I)
    return re.sub(r"\W+", " ", value.lower()).strip()


def is_duplicate(first: dict, second: dict, threshold: float = 0.92) -> bool:
    if first.get("external_message_id") == second.get("external_message_id"):
        return True
    left = f"{normalize_subject(first.get('subject'))} {first.get('body_text', '')[:180]}".lower()
    right = f"{normalize_subject(second.get('subject'))} {second.get('body_text', '')[:180]}".lower()
    return SequenceMatcher(None, left, right).ratio() >= threshold

