"""Thin Google OAuth helpers (authorization URL, code exchange, identity).

Network calls only ever happen when real connectors are enabled and configured,
and a real user is going through the consent flow. Tests mock the connectors and
never reach this module's network code.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from ..config import GOOGLE_READONLY_SCOPES, settings

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"


def build_authorization_url(state: str) -> str:
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_READONLY_SCOPES),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
        "state": state,
    }
    return f"{AUTH_ENDPOINT}?{urlencode(params)}"


def exchange_code(code: str) -> dict[str, Any]:
    import httpx

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = httpx.post(TOKEN_ENDPOINT, data=data, timeout=15)
    response.raise_for_status()
    return response.json()


def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    """Refresh an expired access token without logging either token value."""
    import httpx

    data = {
        "refresh_token": refresh_token,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }
    response = httpx.post(TOKEN_ENDPOINT, data=data, timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_userinfo(access_token: str) -> dict[str, Any]:
    import httpx

    try:
        response = httpx.get(
            USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
    except httpx.HTTPError:
        pass
    return {}
