from __future__ import annotations

import hashlib
import re
from typing import Any


def canonical_subject(subject: str | None, body: str = "") -> str:
    value = subject or body[:72] or "untitled"
    value = re.sub(r"^(re|fw|fwd):\s*", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def thread_key_for(payload: dict[str, Any]) -> str:
    participants = sorted(
        [payload.get("sender_identifier", "")]
        + list(payload.get("recipient_identifiers", []))
    )
    seed = f"{canonical_subject(payload.get('subject'), payload.get('body_text', ''))}|{'|'.join(participants)}"
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()[:20]


def normalize_message(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a fixture message or connector-shaped payload."""
    payload = raw.get("payload", raw)
    body = (
        payload.get("body_text")
        or payload.get("body")
        or payload.get("text")
        or payload.get("description")
        or ""
    )
    sent_at = payload.get("sent_at") or payload.get("start_at") or payload.get("received_at")
    received_at = payload.get("received_at") or sent_at
    normalized = {
        "id": payload.get("id"),
        "raw_message_id": f"raw_{payload.get('id')}",
        "connected_account_id": payload["connected_account_id"],
        "platform": payload["platform"],
        "sender_name": payload.get("sender_name") or payload.get("organizer_name") or "Unknown sender",
        "sender_identifier": payload.get("sender_identifier") or payload.get("organizer") or "unknown",
        "recipient_identifiers": payload.get("recipient_identifiers", []),
        "subject": payload.get("subject") or payload.get("title"),
        "body_text": body.strip(),
        "message_url": payload.get("message_url"),
        "sent_at": sent_at,
        "received_at": received_at,
        "has_attachments": bool(payload.get("has_attachments", False)),
        "is_read": bool(payload.get("is_read", False)),
    }
    normalized["thread_key"] = payload.get("thread_key") or thread_key_for(normalized)
    return normalized

