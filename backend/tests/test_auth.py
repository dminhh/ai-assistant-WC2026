import pytest
from app.services.auth import hash_password, verify_password, create_token, decode_token


def test_password_hash_and_verify():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    token = create_token(user_id=42)
    payload = decode_token(token)
    assert payload["sub"] == 42
