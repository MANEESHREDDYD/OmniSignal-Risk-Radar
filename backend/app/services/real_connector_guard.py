"""Safety guard for real (non-demo) connector endpoints.

Real OAuth and real sync must never run unless the user has explicitly opted in
via ``REAL_CONNECTORS_ENABLED=true``. These helpers raise typed errors that
routers translate into safe, audited "blocked" responses — never crashes.
"""

from __future__ import annotations

from ..config import settings


class RealConnectorsDisabledError(Exception):
    """Real connectors are turned off; synthetic demo mode is active."""

    status = "blocked_disabled"
    message = (
        "Real connectors are disabled. Synthetic demo mode is active. "
        "Set REAL_CONNECTORS_ENABLED=true locally to enable real Google access."
    )


class MissingConnectorConfigError(Exception):
    """Real connectors are enabled but required configuration is missing."""

    status = "blocked_missing_config"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def ensure_real_connectors_enabled() -> None:
    """Block unless REAL_CONNECTORS_ENABLED is explicitly true."""
    if settings.REAL_CONNECTORS_ENABLED is not True:
        raise RealConnectorsDisabledError()


def ensure_google_configured() -> None:
    """Block unless Google OAuth client config and the token key are present."""
    ensure_real_connectors_enabled()
    if not settings.google_oauth_configured:
        raise MissingConnectorConfigError(
            "Google OAuth client is not configured. Set GOOGLE_CLIENT_ID, "
            "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI in your .env."
        )
    if not settings.token_encryption_configured:
        raise MissingConnectorConfigError(
            "TOKEN_ENCRYPTION_KEY is required to store real OAuth tokens securely."
        )
