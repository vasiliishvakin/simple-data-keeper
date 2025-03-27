import asyncio
from typing import AsyncIterator

from app.storage.base import StorageDriver
from app.utils.helpers import _to_stream


class FileService:
    def __init__(self, driver: StorageDriver):
        self.driver = driver

    async def save_file(self, file_id: str, stream: AsyncIterator[bytes]) -> None:
        await self.driver.save(file_id, stream)

    async def save_file_with_hash_check(
        self,
        file_id: str,
        stream: AsyncIterator[bytes],
        expected_hash: str,
        algorithm: str,
    ) -> None:
        await self.driver.save(file_id, stream)
        actual_hash = await self.driver.hash(file_id, algorithm)
        if actual_hash != expected_hash:
            raise ValueError(f"Hash mismatch: expected {expected_hash}, got {actual_hash}")

    async def save_file_background(self, file_id: str, stream: AsyncIterator[bytes]) -> None:
        content = [chunk async for chunk in stream]
        task = asyncio.create_task(self._save_silent(file_id, b"".join(content)))
        try:
            await asyncio.wait_for(task, timeout=0.1)
        except asyncio.TimeoutError:
            pass  # Task is running in background

    async def _save_silent(self, file_id: str, content: bytes) -> None:
        try:
            await self.driver.save(file_id, _to_stream(content))
        except Exception:
            pass

    async def get_file(self, filename: str):
        return {"filename": filename, "content": self.driver.read(filename)}

    async def read_file_fully(self, filename: str) -> bytes:
        chunks = []
        async for chunk in self.driver.read(filename):
            chunks.append(chunk)
        return b"".join(chunks)

    async def delete_file(self, filename: str):
        return await self.driver.delete(filename)

    async def delete_file_checked(self, filename: str):
        if not await self.driver.exists(filename):
            raise RuntimeError(f"File '{filename}' does not exist before deletion")
        await self.driver.delete(filename)
        if await self.driver.exists(filename):
            raise RuntimeError(f"File '{filename}' was not deleted")

    async def check_file_exists(self, filename: str):
        return await self.driver.exists(filename)

    async def get_file_size(self, filename: str):
        return await self.driver.size(filename)

    async def get_file_hash(self, filename: str, algorithm: str):
        return await self.driver.hash(filename, algorithm)
