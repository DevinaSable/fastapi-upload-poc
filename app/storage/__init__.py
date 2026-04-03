from app.storage.base import BaseStorage
from app.core.config import get_settings

settings = get_settings()


def get_storage() -> BaseStorage:
    """Returns the correct storage backend based on environment."""
    if settings.STORAGE_BACKEND == "azure":
        from app.storage.azure_blob import AzureBlobStorage
        return AzureBlobStorage()
    from app.storage.local import LocalStorage
    return LocalStorage()