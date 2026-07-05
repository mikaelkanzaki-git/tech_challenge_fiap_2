from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


def verify_password(
    plain_password: str,
    password_hash: str,
    password_salt: str,
    password_iterations: int,
) -> bool:
    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        password_salt.encode("utf-8"),
        password_iterations,
    ).hex()
    return hmac.compare_digest(candidate_hash, password_hash)


def create_access_token(
    subject: str,
    secret_key: str,
    expires_minutes: int,
    issued_at: int | None = None,
) -> str:
    issued_at_timestamp = issued_at or int(time.time())
    payload = {
        "sub": subject,
        "iat": issued_at_timestamp,
        "exp": issued_at_timestamp + expires_minutes * 60,
        "token_type": "access",
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_encode_json(header)}.{_encode_json(payload)}"
    signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_base64_url_encode(signature)}"


def decode_access_token(token: str, secret_key: str, current_time: int | None = None) -> dict[str, Any]:
    try:
        header_text, payload_text, signature_text = token.split(".")
    except ValueError as exc:
        raise ValueError("Token invalido.") from exc

    signing_input = f"{header_text}.{payload_text}"
    expected_signature = hmac.new(
        secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    received_signature = _base64_url_decode(signature_text)

    if not hmac.compare_digest(received_signature, expected_signature):
        raise ValueError("Assinatura do token invalida.")

    header = json.loads(_base64_url_decode(header_text))
    if header.get("alg") != "HS256":
        raise ValueError("Algoritmo do token invalido.")

    payload = json.loads(_base64_url_decode(payload_text))
    expiration_timestamp = int(payload.get("exp", 0))
    if expiration_timestamp < (current_time or int(time.time())):
        raise ValueError("Token expirado.")

    return payload


def _encode_json(value: dict[str, Any]) -> str:
    raw_json = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _base64_url_encode(raw_json)


def _base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _base64_url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
