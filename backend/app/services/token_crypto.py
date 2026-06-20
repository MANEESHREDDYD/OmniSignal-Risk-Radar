"""Symmetric encryption for OAuth tokens at rest.

Uses Fernet (AES-128-CBC + HMAC) with a locally generated ``TOKEN_ENCRYPTION_KEY``.
Plaintext tokens are never logged and never returned to the frontend.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from ..config import settings


class TokenCryptoError(Exception):
    """Raised when encryption/decryption cannot be performed safely."""


class MissingEncryptionKeyError(TokenCryptoError):
    """Raised when TOKEN_ENCRYPTION_KEY is required but not configured."""


def generate_key() -> str:
    """Generate a new Fernet key (for local setup, never committed)."""
    return Fernet.generate_key().decode("utf-8")


def _fernet() -> Fernet:
    key = settings.TOKEN_ENCRYPTION_KEY
    if not key:
        raise MissingEncryptionKeyError(
            "TOKEN_ENCRYPTION_KEY is not set. Generate one locally and add it to "
            "your .env before storing real OAuth tokens."
        )
    try:
        return Fernet(key.encode("utf-8"))
    except (ValueError, TypeError) as exc:  # malformed key
        raise TokenCryptoError("TOKEN_ENCRYPTION_KEY is malformed (expect a Fernet key).") from exc


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token string. Returns ciphertext that differs from plaintext."""
    if plaintext is None:
        raise TokenCryptoError("Cannot encrypt a None token.")
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a previously encrypted token. Raises on tamper/bad key."""
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise TokenCryptoError("Failed to decrypt token (invalid key or corrupted data).") from exc
