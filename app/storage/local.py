import hashlib
import os
from collections.abc import AsyncIterator

import aiofiles

from app.storage.base import StorageDriver
from app.utils.config_validation import validate_files_local_base_dir
from app.utils.helpers import safe_join


class LocalFileDriver(StorageDriver):
    def __init__(self, base_dir: str, default_chunk_size: int = 8192):
        self.base_dir = validate_files_local_base_dir(base_dir)
        self.chunk_size = default_chunk_size

    def _full_path(self, path: str) -> str:
        return safe_join(self.base_dir, path)

    async def save(self, path: str, stream: AsyncIterator[bytes]) -> None:
        full_path = self._full_path(path)
        async with aiofiles.open(full_path, "wb") as f:
            async for chunk in stream:
                await f.write(chunk)

    async def read(self, path: str, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        full_path = self._full_path(path)
        chunk_size = chunk_size or self.chunk_size

        async with aiofiles.open(full_path, "rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    async def delete(self, path: str) -> None:
        full_path = self._full_path(path)
        try:
            os.remove(full_path)
        except FileNotFoundError:
            pass

    async def exists(self, path: str) -> bool:
        full_path = self._full_path(path)
        return os.path.exists(full_path)

    async def size(self, path: str) -> int:
        full_path = self._full_path(path)
        return os.path.getsize(full_path)

    async def hash(
        self,
        path: str,
        algorithm: str,
        chunk_size: int | None = None,
    ) -> str:
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

        hash_func = hashlib.new(algorithm)

        async for chunk in self.read(path, chunk_size):
            hash_func.update(chunk)

        return hash_func.hexdigest()
