import os
import aiofiles
from app.storage.base import BaseStorage
from app.core.config import get_settings

settings = get_settings()


class LocalStorage(BaseStorage):
    async def save(self, filename: str, content: bytes) -> str:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        path = os.path.join(settings.UPLOAD_DIR, filename)
        async with aiofiles.open(path, "wb") as f:
            await f.write(content)
        return path

    async def delete(self, path: str) -> None:
        if os.path.exists(path):
            os.remove(path)