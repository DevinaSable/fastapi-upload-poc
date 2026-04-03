from fastapi import APIRouter, HTTPException, status
import bcrypt
from app.models.schemas import LoginRequest, TokenResponse
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# 🔒 In prod: replace with DB lookup
FAKE_USERS_DB = {
    "devd": bcrypt.hashpw(b"secret123", bcrypt.gensalt()),
}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    hashed = FAKE_USERS_DB.get(body.username)
    if not hashed or not bcrypt.checkpw(body.password.encode(), hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": body.username})
    return TokenResponse(access_token=token)