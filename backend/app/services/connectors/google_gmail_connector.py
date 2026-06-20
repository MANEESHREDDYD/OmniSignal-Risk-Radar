"""Read-only Gmail connector.

Converts Gmail API message resources into the app's normalized-raw payload shape.
The Google client is injected so tests can pass a mock — this module never makes
network calls itself, and only ever reads. It does not send, modify, label, or
delete messages, and it does not download attachments.
"""

from __future__ import annotations

import base64
import binascii
from typing import Any, Protocol

# Cap stored body text so we never persist huge payloads.
MAX_BODY_CHARS = 4000
DEFAULT_MAX_RESULTS = 25


class GmailClient(Protocol):
    """Minimal read-only surface the connector depends on."""

    def list_messages(self, max_results: int) -> dict[str, Any]:
        ...

    def get_message(self, message_id: str) -> dict[str, Any]:
        ...


def _decode_b64url(data: str | None) -> str:
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="replace")
    except (binascii.Error, ValueError):
        return ""


def _header(headers: list[dict[str, str]], name: str) -> str:
    lowered = name.lower()
    for item in headers or []:
        if (item.get("name") or "").lower() == lowered:
            return item.get("value") or ""
    return ""


def _split_address(value: str) -> tuple[str, str]:
    """Parse 'Name <email>' into (name, email)."""
    value = (value or "").strip()
    if "<" in value and ">" in value:
        name = value.split("<", 1)[0].strip().strip('"')
        email = value.split("<", 1)[1].split(">", 1)[0].strip()
        return (name or email, email)
    return (value, value)


def _extract_plain_body(payload: dict[str, Any]) -> str:
    """Walk MIME parts to find text/plain (falls back to top-level body)."""
    if not payload:
        return ""
    mime = payload.get("mimeType", "")
    body = payload.get("body", {}) or {}
    if mime == "text/plain" and body.get("data"):
        return _decode_b64url(body["data"])
    for part in payload.get("parts", []) or []:
        text = _extract_plain_body(part)
        if text:
            return text
    if body.get("data"):
        return _decode_b64url(body["data"])
    return ""


def _to_iso_from_internal(internal_date_ms: str | None) -> str | None:
    if not internal_date_ms:
        return None
    try:
        from datetime import datetime, timezone

        return datetime.fromtimestamp(int(internal_date_ms) / 1000, tz=timezone.utc).isoformat()
    except (ValueError, TypeError, OSError):
        return None


def normalize_gmail_message(resource: dict[str, Any], connected_account_id: str) -> dict[str, Any]:
    """Convert a single Gmail message resource into a normalized-raw payload."""
    payload = resource.get("payload", {}) or {}
    headers = payload.get("headers", []) or []
    sender_name, sender_email = _split_address(_header(headers, "From"))
    recipients = [
        _split_address(addr)[1]
        for addr in _header(headers, "To").split(",")
        if addr.strip()
    ]
    subject = _header(headers, "Subject") or None
    body = _extract_plain_body(payload) or resource.get("snippet", "") or ""
    body = body.strip()[:MAX_BODY_CHARS]
    sent_at = _to_iso_from_internal(resource.get("internalDate")) or _header(headers, "Date") or None
    provider_id = resource.get("id", "")
    label_ids = resource.get("labelIds", []) or []
    return {
        "id": f"gmail_{provider_id}",
        "external_message_id": f"gmail:{provider_id}",
        "connected_account_id": connected_account_id,
        "platform": "gmail",
        "category": "real_gmail",
        "sender_name": sender_name or "Unknown sender",
        "sender_identifier": sender_email or "unknown",
        "recipient_identifiers": recipients,
        "subject": subject,
        "body_text": body,
        "thread_key": f"gmail_thread_{resource.get('threadId', provider_id)}",
        "sent_at": sent_at,
        "received_at": sent_at,
        "has_attachments": False,
        "is_read": "UNREAD" not in label_ids,
        # Provider metadata kept for traceability (no secrets, body truncated above).
        "provider_resource_id": provider_id,
        "labels": label_ids,
    }


class GoogleGmailConnector:
    """Read-only Gmail connector that depends on an injected client."""

    platform = "gmail"

    def __init__(self, client: GmailClient) -> None:
        self.client = client

    def fetch_messages(self, max_results: int = DEFAULT_MAX_RESULTS) -> list[dict[str, Any]]:
        """Return raw provider resources for a small, safe batch."""
        max_results = max(1, min(max_results, DEFAULT_MAX_RESULTS))
        listing = self.client.list_messages(max_results=max_results) or {}
        refs = listing.get("messages", []) or []
        resources: list[dict[str, Any]] = []
        for ref in refs[:max_results]:
            message_id = ref.get("id")
            if not message_id:
                continue
            resource = self.client.get_message(message_id)
            if resource:
                resources.append(resource)
        return resources

    def fetch_normalized(
        self, connected_account_id: str, max_results: int = DEFAULT_MAX_RESULTS
    ) -> list[dict[str, Any]]:
        """Return normalized-raw payloads ready for ingestion. Skips malformed."""
        normalized: list[dict[str, Any]] = []
        for resource in self.fetch_messages(max_results=max_results):
            try:
                normalized.append(normalize_gmail_message(resource, connected_account_id))
            except (KeyError, AttributeError, TypeError):
                # Malformed message — skip safely rather than failing the batch.
                continue
        return normalized
