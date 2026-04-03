from datetime import datetime, timedelta, timezone
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.session import get_db
from app.models.db_models import RefreshToken, User
from app.models.schemas import (
    AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_LOGIN)        # 🔒 5 attempts/min per IP
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Lookup user
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    if not user or not bcrypt.checkpw(body.password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Account disabled")

    # Create tokens
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token()

    # Store refresh token in DB
    db.add(RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    ))
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    # Lookup token in DB
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == body.refresh_token)
    )
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")

    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token expired")

    # Rotate — revoke old, issue new access token
    db_token.revoked = True
    await db.commit()

    # Lookup user
    result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = result.scalar_one_or_none()

    return AccessTokenResponse(access_token=create_access_token({"sub": user.username}))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke refresh token — effectively logs the user out."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == body.refresh_token)
    )
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.revoked = True
        await db.commit()