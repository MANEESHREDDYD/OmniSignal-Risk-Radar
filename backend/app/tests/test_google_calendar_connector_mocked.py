from app.services.connectors.google_calendar_connector import (
    GoogleCalendarConnector,
    normalize_calendar_event,
)


class FakeCalendarClient:
    """Read-only mock. Exposes NO create/update/delete methods."""

    def __init__(self, items):
        self._items = items
        self.calls = []

    def list_events(self, time_min, time_max, max_results):
        self.calls.append(("list_events", time_min, time_max, max_results))
        return {"items": self._items}


TIMED_EVENT = {
    "id": "e1",
    "summary": "Design review",
    "description": "Discuss V1.1 connector.",
    "location": "Room 4",
    "hangoutLink": "https://meet.google.com/abc-defg-hij",
    "status": "confirmed",
    "organizer": {"email": "boss@example.com", "displayName": "The Boss"},
    "attendees": [{"email": "me@example.com"}, {"email": "peer@example.com"}],
    "start": {"dateTime": "2026-07-01T15:00:00Z"},
    "end": {"dateTime": "2026-07-01T16:00:00Z"},
}

ALL_DAY_EVENT = {
    "id": "e2",
    "summary": "Company holiday",
    "status": "confirmed",
    "organizer": {"email": "hr@example.com"},
    "start": {"date": "2026-07-04"},
    "end": {"date": "2026-07-05"},
}


def test_converts_mocked_events_to_normalized():
    connector = GoogleCalendarConnector(FakeCalendarClient([TIMED_EVENT]))
    items = connector.fetch_normalized("acct_1")
    assert len(items) == 1
    item = items[0]
    assert item["platform"] == "calendar"
    assert item["subject"] == "Design review"
    assert item["event_start"] == "2026-07-01T15:00:00Z"
    assert item["event_conference_link"].startswith("https://meet.google.com/")
    assert "peer@example.com" in item["event_attendees"]
    assert item["external_message_id"] == "gcal:e1"


def test_connector_only_uses_read_methods():
    client = FakeCalendarClient([TIMED_EVENT])
    GoogleCalendarConnector(client).fetch_normalized("acct_1")
    assert all(name == "list_events" for name, *_ in client.calls)
    assert not hasattr(client, "insert_event")
    assert not hasattr(client, "delete_event")


def test_handles_empty_calendar():
    assert GoogleCalendarConnector(FakeCalendarClient([])).fetch_normalized("acct_1") == []


def test_handles_all_day_event():
    item = normalize_calendar_event(ALL_DAY_EVENT, "acct_1")
    assert item["event_start"] == "2026-07-04"
    assert item["subject"] == "Company holiday"
