import pytest

from triage_api.core.security import create_access_token, decode_access_token, verify_password


def test_verify_password_returns_true_for_matching_hash() -> None:
    assert verify_password(
        plain_password="fiap@Tech_2",
        password_hash="139469b8f294c7212ca901e29a3dca86b68a0803c5c362e6b6baf3f0711b3e06",
        password_salt="tech_challenge_fiap_2_fiap_user",
        password_iterations=260000,
    )


def test_access_token_round_trip() -> None:
    token = create_access_token(
        subject="fiap@tech2.com",
        secret_key="test-secret",
        expires_minutes=60,
        issued_at=1000,
    )

    payload = decode_access_token(token, secret_key="test-secret", current_time=1001)

    assert payload["sub"] == "fiap@tech2.com"
    assert payload["token_type"] == "access"


def test_decode_access_token_rejects_invalid_signature() -> None:
    token = create_access_token(
        subject="fiap@tech2.com",
        secret_key="test-secret",
        expires_minutes=60,
        issued_at=1000,
    )

    with pytest.raises(ValueError, match="Assinatura"):
        decode_access_token(token, secret_key="wrong-secret", current_time=1001)


def test_decode_access_token_rejects_expired_token() -> None:
    token = create_access_token(
        subject="fiap@tech2.com",
        secret_key="test-secret",
        expires_minutes=1,
        issued_at=1000,
    )

    with pytest.raises(ValueError, match="Token expirado"):
        decode_access_token(token, secret_key="test-secret", current_time=2000)
