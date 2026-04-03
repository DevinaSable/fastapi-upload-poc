from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """All storage backends must implement this interface."""

    @abstractmethod
    async def save(self, filename: str, content: bytes) -> str:
        """Save file and return its storage path/URL."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete a file by its storage path."""
        ...