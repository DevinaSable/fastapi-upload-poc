from azure.storage.blob.aio import BlobServiceClient
from app.storage.base import BaseStorage
from app.core.config import get_settings

settings = get_settings()


class AzureBlobStorage(BaseStorage):
    def __init__(self):
        self._client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self._container = settings.AZURE_STORAGE_CONTAINER_NAME

    async def save(self, filename: str, content: bytes) -> str:
        async with self._client:
            container = self._client.get_container_client(self._container)
            await container.upload_blob(name=filename, data=content, overwrite=True)
        return f"https://{self._client.account_name}.blob.core.windows.net/{self._container}/{filename}"

    async def delete(self, path: str) -> None:
        filename = path.split("/")[-1]
        async with self._client:
            container = self._client.get_container_client(self._container)
            await container.delete_blob(filename)