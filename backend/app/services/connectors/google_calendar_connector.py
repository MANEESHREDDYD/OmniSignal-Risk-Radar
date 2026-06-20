"""Read-only Google Calendar connector.

Converts Calendar API event resources into the app's normalized-raw payload shape.
The Google client is injected so tests can pass a mock. This module never makes
network calls itself and only ever reads — it does not create, update, delete
events, and it does not send RSVP responses.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

MAX_BODY_CHARS = 4000
DEFAULT_MAX_RESULTS = 25
# Default safe window: next 14 days and past 3 days.
DEFAULT_DAYS_AHEAD = 14
DEFAULT_DAYS_BEHIND = 3


class CalendarClient(Protocol):
    """Minimal read-only surface the connector depends on."""

    def list_events(self, time_min: str, time_max: str, max_results: int) -> dict[str, Any]:
        ...


def default_window(now: datetime | None = None) -> tuple[str, str]:
    now = now or datetime.now(timezone.utc)
    time_min = (now - timedelta(days=DEFAULT_DAYS_BEHIND)).isoformat()
    time_max = (now + timedelta(days=DEFAULT_DAYS_AHEAD)).isoformat()
    return time_min, time_max


def _event_time(node: dict[str, Any] | None) -> str | None:
    if not node:
        return None
    # All-day events use "date"; timed events use "dateTime".
    return node.get("dateTime") or node.get("date")


def normalize_calendar_event(resource: dict[str, Any], connected_account_id: str) -> dict[str, Any]:
    """Convert a single Calendar event resource into a normalized-raw payload."""
    event_id = resource.get("id", "")
    title = resource.get("summary") or "(no title)"
    organizer = resource.get("organizer", {}) or {}
    attendees = [
        a.get("email")
        for a in (resource.get("attendees", []) or [])
        if a.get("email")
    ]
    start = _event_time(resource.get("start"))
    end = _event_time(resource.get("end"))
    location = resource.get("location")
    conference = resource.get("hangoutLink") or (
        (resource.get("conferenceData", {}) or {}).get("entryPoints", [{}])[0].get("uri")
        if resource.get("conferenceData")
        else None
    )
    body_lines = [
        f"Calendar event: {title}",
        f"When: {start} to {end}",
    ]
    if location:
        body_lines.append(f"Location: {location}")
    if conference:
        body_lines.append(f"Conference link: {conference}")
    if attendees:
        body_lines.append(f"Attendees: {', '.join(attendees)}")
    description = resource.get("description")
    if description:
        body_lines.append(description)
    body_text = "\n".join(body_lines).strip()[:MAX_BODY_CHARS]

    return {
        "id": f"gcal_{event_id}",
        "external_message_id": f"gcal:{event_id}",
        "connected_account_id": connected_account_id,
        "platform": "calendar",
        "category": "real_calendar",
        "sender_name": organizer.get("displayName") or organizer.get("email") or "Calendar",
        "sender_identifier": organizer.get("email") or "calendar",
        "recipient_identifiers": attendees,
        "subject": title,
        "body_text": body_text,
        "thread_key": f"gcal_event_{event_id}",
        "sent_at": start,
        "received_at": start,
        "has_attachments": False,
        "is_read": False,
        # Event metadata for downstream conflict/deadline logic & traceability.
        "provider_resource_id": event_id,
        "event_start": start,
        "event_end": end,
        "event_location": location,
        "event_conference_link": conference,
        "event_status": resource.get("status"),
        "event_attendees": attendees,
    }


class GoogleCalendarConnector:
    """Read-only Calendar connector that depends on an injected client."""

    platform = "calendar"

    def __init__(self, client: CalendarClient) -> None:
        self.client = client

    def fetch_events(
        self,
        time_min: str | None = None,
        time_max: str | None = None,
        max_results: int = DEFAULT_MAX_RESULTS,
    ) -> list[dict[str, Any]]:
        if time_min is None or time_max is None:
            time_min, time_max = default_window()
        max_results = max(1, min(max_results, DEFAULT_MAX_RESULTS))
        listing = self.client.list_events(
            time_min=time_min, time_max=time_max, max_results=max_results
        ) or {}
        return (listing.get("items", []) or [])[:max_results]

    def fetch_normalized(
        self,
        connected_account_id: str,
        time_min: str | None = None,
        time_max: str | None = None,
        max_results: int = DEFAULT_MAX_RESULTS,
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for resource in self.fetch_events(time_min, time_max, max_results):
            try:
                normalized.append(normalize_calendar_event(resource, connected_account_id))
            except (KeyError, AttributeError, TypeError):
                continue
        return normalized
