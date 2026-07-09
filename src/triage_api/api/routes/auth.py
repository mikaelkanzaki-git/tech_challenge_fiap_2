from __future__ import annotations

from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError

from triage_api.core.config import settings
from triage_api.core.logging import get_logger
from triage_api.core.security import create_access_token, verify_password
from triage_api.schemas.auth import TokenRequest, TokenResponse

router = APIRouter(tags=["auth"])
logger = get_logger(__name__)


@router.post("/token", response_model=TokenResponse)
@router.post("/login", response_model=TokenResponse)
async def create_token(request: Request) -> TokenResponse:
    token_request = await _read_token_request(request)
    logger.info(
        "Tentativa de autenticacao recebida.",
        extra={"step": "auth_login_received", "payload": {"username": token_request.username}},
    )

    user_repository = request.app.state.user_repository
    if user_repository is None:
        logger.error(
            "Repositório de usuários não configurado.",
            extra={"step": "auth_repository_missing", "payload": {"username": token_request.username}},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repositório de usuários não configurado.",
        )

    user = user_repository.get_user_by_email(token_request.username)
    if user is None or not user.is_active or not verify_password(
        token_request.password,
        user.password_hash,
        user.password_salt,
        user.password_iterations,
    ):
        logger.warning(
            "Credenciais invalidas.",
            extra={"step": "auth_login_failed", "payload": {"username": token_request.username}},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.email,
        secret_key=settings.jwt_secret_key,
        expires_minutes=settings.access_token_expire_minutes,
    )
    logger.info(
        "Autenticacao realizada com sucesso.",
        extra={"step": "auth_login_completed", "payload": {"username": token_request.username}},
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def _read_token_request(request: Request) -> TokenRequest:
    content_type = request.headers.get("content-type", "")
    try:
        if "application/json" in content_type:
            payload = await request.json()
        else:
            body = (await request.body()).decode("utf-8")
            parsed_body = parse_qs(body)
            payload = {
                "username": _first_value(parsed_body, "username"),
                "password": _first_value(parsed_body, "password"),
            }
        return TokenRequest.model_validate(payload)
    except (ValidationError, UnicodeDecodeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Informe usuário e senha para autenticação.",
        ) from None


def _first_value(values: dict[str, list[str]], key: str) -> str | None:
    item = values.get(key)
    if not item:
        return None
    return item[0]
