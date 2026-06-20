"""Runtime configuration for OmniSignal Risk Radar.

Values are read from the environment on every access so that tests can toggle
flags with ``monkeypatch.setenv`` without reloading modules. Synthetic demo mode
stays fully functional even when none of the real-connector values are set.
"""

from __future__ import annotations

import os

# Read-only Google scopes. We never request modify/send/write scopes.
GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
CALENDAR_EVENTS_READONLY_SCOPE = "https://www.googleapis.com/auth/calendar.events.readonly"
CALENDAR_LIST_READONLY_SCOPE = "https://www.googleapis.com/auth/calendar.calendarlist.readonly"

GOOGLE_READONLY_SCOPES = [
    GMAIL_READONLY_SCOPE,
    CALENDAR_EVENTS_READONLY_SCOPE,
    CALENDAR_LIST_READONLY_SCOPE,
]


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Environment-backed settings accessor (always reads live values)."""

    @property
    def DEMO_MODE(self) -> bool:
        return _as_bool(os.getenv("DEMO_MODE"), default=True)

    @property
    def REAL_CONNECTORS_ENABLED(self) -> bool:
        return _as_bool(os.getenv("REAL_CONNECTORS_ENABLED"), default=False)

    @property
    def GOOGLE_CLIENT_ID(self) -> str:
        return os.getenv("GOOGLE_CLIENT_ID", "").strip()

    @property
    def GOOGLE_CLIENT_SECRET(self) -> str:
        return os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

    @property
    def GOOGLE_REDIRECT_URI(self) -> str:
        return os.getenv(
            "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback"
        ).strip()

    @property
    def TOKEN_ENCRYPTION_KEY(self) -> str:
        return os.getenv("TOKEN_ENCRYPTION_KEY", "").strip()

    @property
    def FRONTEND_ORIGIN(self) -> str:
        return os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").strip()

    @property
    def google_oauth_configured(self) -> bool:
        """True when the minimum Google OAuth client config is present."""
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET and self.GOOGLE_REDIRECT_URI)

    @property
    def token_encryption_configured(self) -> bool:
        return bool(self.TOKEN_ENCRYPTION_KEY)


settings = Settings()
