from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from triage_api.core.config import settings
from triage_api.core.security import decode_access_token
from triage_api.schemas.auth import AuthenticatedUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token, settings.jwt_secret_key)
    except ValueError as exc:
        raise credentials_exception from exc

    email = payload.get("sub")
    if not isinstance(email, str) or not email:
        raise credentials_exception

    user_repository = request.app.state.user_repository
    if user_repository is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repositório de usuários não configurado.",
        )

    user = user_repository.get_user_by_email(email)
    if user is None or not user.is_active:
        raise credentials_exception

    return AuthenticatedUser(email=user.email)
