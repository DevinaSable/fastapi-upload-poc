from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.init_db import init_db
from app.routers import auth, upload

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()          # create tables on startup
    yield                    # app runs here
    # cleanup on shutdown goes here if needed


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — tighten origins in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}