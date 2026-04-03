from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext
from app.models.schemas import LoginRequest, TokenResponse
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔒 In prod: replace with DB lookup
FAKE_USERS_DB = {
    "devd": pwd_context.hash("secret123"),
}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    hashed = FAKE_USERS_DB.get(body.username)
    if not hashed or not pwd_context.verify(body.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": body.username})
    return TokenResponse(access_token=token)