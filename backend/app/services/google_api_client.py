"""Read-only HTTP clients for Gmail and Calendar REST APIs.

These satisfy the connector ``GmailClient`` / ``CalendarClient`` protocols using a
bearer access token. Only GET requests are issued — no send, modify, or write
calls exist here. Used only at real-sync time; tests inject mocks instead.
"""

from __future__ import annotations

from typing import Any

GMAIL_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
CALENDAR_BASE = "https://www.googleapis.com/calendar/v3/calendars/primary"


class GmailHttpClient:
    def __init__(self, access_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {access_token}"}

    def list_messages(self, max_results: int) -> dict[str, Any]:
        import httpx

        response = httpx.get(
            f"{GMAIL_BASE}/messages",
            headers=self._headers,
            params={"maxResults": max_results},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def get_message(self, message_id: str) -> dict[str, Any]:
        import httpx

        response = httpx.get(
            f"{GMAIL_BASE}/messages/{message_id}",
            headers=self._headers,
            params={"format": "full"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()


class CalendarHttpClient:
    def __init__(self, access_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {access_token}"}

    def list_events(self, time_min: str, time_max: str, max_results: int) -> dict[str, Any]:
        import httpx

        response = httpx.get(
            f"{CALENDAR_BASE}/events",
            headers=self._headers,
            params={
                "timeMin": time_min,
                "timeMax": time_max,
                "maxResults": max_results,
                "singleEvents": "true",
                "orderBy": "startTime",
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
