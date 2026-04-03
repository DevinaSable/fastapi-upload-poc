from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from app.auth.dependencies import get_current_user
from app.core.config import get_settings
from app.core.limiter import limiter
from app.models.schemas import UploadResponse
from app.storage import get_storage

router = APIRouter(prefix="/files", tags=["files"])
settings = get_settings()


def _validate_file(file: UploadFile) -> None:
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Extension '.{ext}' not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )


@router.post("/upload", response_model=UploadResponse)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)       # 🔒 20 uploads/min per IP
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    _validate_file(file)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    storage = get_storage()
    path = await storage.save(file.filename, content)

    return UploadResponse(
        filename=file.filename,
        size_bytes=len(content),
        storage_path=path,
        message=f"Uploaded by {current_user['sub']}",
    )