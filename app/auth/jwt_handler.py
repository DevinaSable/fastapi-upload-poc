import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import get_settings

settings = get_settings()


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token() -> str:
    """Cryptographically secure random token — stored in DB."""
    return secrets.token_urlsafe(64)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "access":
            return {}
        return payload
    except JWTError:
        return {}