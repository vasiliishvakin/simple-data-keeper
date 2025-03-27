from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class StorageDriver(ABC):
    @abstractmethod
    async def save(self, path: str, stream: AsyncIterator[bytes]) -> None: ...

    @abstractmethod
    async def read(self, path: str, chunk_size: int | None = None) -> AsyncIterator[bytes]: ...

    @abstractmethod
    async def delete(self, path: str) -> None: ...

    @abstractmethod
    async def exists(self, path: str) -> bool: ...

    @abstractmethod
    async def size(self, path: str) -> int: ...

    @abstractmethod
    async def hash(self, path: str, algorithm: str, chunk_size: int | None = None) -> str: ...
