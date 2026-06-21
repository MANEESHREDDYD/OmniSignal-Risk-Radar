import pytest

from app.services import token_crypto
from app.services.token_crypto import (
    MissingEncryptionKeyError,
    TokenCryptoError,
    decrypt_token,
    encrypt_token,
    generate_key,
)


def test_encrypt_then_decrypt_roundtrip(token_key):
    secret = "mock-access-token-value"
    ciphertext = encrypt_token(secret)
    assert ciphertext != secret  # never stored as plaintext
    assert secret not in ciphertext
    assert decrypt_token(ciphertext) == secret


def test_two_encryptions_differ_but_decrypt_equal(token_key):
    a = encrypt_token("same-value")
    b = encrypt_token("same-value")
    assert a != b  # Fernet includes IV/timestamp
    assert decrypt_token(a) == decrypt_token(b) == "same-value"


def test_missing_key_blocks_encryption(monkeypatch):
    monkeypatch.delenv("TOKEN_ENCRYPTION_KEY", raising=False)
    with pytest.raises(MissingEncryptionKeyError):
        encrypt_token("anything")


def test_malformed_key_raises(monkeypatch):
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", "not-a-valid-fernet-key")
    with pytest.raises(TokenCryptoError):
        encrypt_token("anything")


def test_generate_key_is_usable(monkeypatch):
    key = generate_key()
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", key)
    assert decrypt_token(encrypt_token("hi")) == "hi"
