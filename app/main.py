from fastapi import FastAPI
from app.core.config import get_settings
from app.routers import auth, upload

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,   # hide Swagger in prod
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.include_router(auth.router)
app.include_router(upload.router)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}