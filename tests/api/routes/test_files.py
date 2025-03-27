import asyncio
from hashlib import sha256
from pathlib import Path

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.config.settings import Settings


@pytest.mark.asyncio
async def test_upload_file_basic(app, override_settings: Settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-File-Id": "file1.txt"}
        content = b"Hello, world!"
        response = await ac.post("/files", headers=headers, content=content)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        saved_path = Path(override_settings.base_dir) / "file1.txt"
        assert saved_path.read_bytes() == content


@pytest.mark.asyncio
async def test_upload_file_with_hash(app, override_settings: Settings):
    content = b"Content with hash verification"
    file_hash = sha256(content).hexdigest()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-File-Id": "hashed_file.txt", "X-File-Hash": file_hash, "X-File-Hash-Algorithm": "sha256"}
        response = await ac.post("/files", headers=headers, content=content)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        saved_path = Path(override_settings.base_dir) / "hashed_file.txt"
        assert saved_path.read_bytes() == content


@pytest.mark.asyncio
async def test_upload_file_with_invalid_hash(app):
    content = b"Content with wrong hash"
    wrong_hash = "wrong_hash_value"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-File-Id": "invalid_hash.txt", "X-File-Hash": wrong_hash, "X-File-Hash-Algorithm": "sha256"}
        response = await ac.post("/files", headers=headers, content=content)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "hash mismatch" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_file_background(app, override_settings: Settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-File-Id": "background_file.txt"}
        content = b"Background upload content"
        response = await ac.post("/files", headers=headers, content=content, params={"background": True})

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Give some time for background task to complete
        await asyncio.sleep(0.1)
        saved_path = Path(override_settings.base_dir) / "background_file.txt"
        assert saved_path.read_bytes() == content


@pytest.mark.asyncio
async def test_upload_file_missing_file_id(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/files", content=b"Some content")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_upload_empty_file(app, override_settings: Settings):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-File-Id": "empty.txt"}
        response = await ac.post("/files", headers=headers, content=b"")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        saved_path = Path(override_settings.base_dir) / "empty.txt"
        assert saved_path.read_bytes() == b""


@pytest.mark.asyncio
async def test_get_file_success(app, override_settings: Settings):
    # First upload a file
    file_id = "test_read.txt"
    content = b"Hello, this is a test file!"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Upload the file
        headers = {"X-File-Id": file_id}
        await ac.post("/files", headers=headers, content=content)

        # Read the file back
        response = await ac.get(f"/files/{file_id}")

        assert response.status_code == 200
        assert response.content == content
        assert response.headers["content-type"] == "application/octet-stream"
        assert response.headers["content-disposition"] == f'attachment; filename="{file_id}"'


@pytest.mark.asyncio
async def test_get_file_not_found(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/files/nonexistent.txt")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_file_success(app, override_settings: Settings):
    # First upload a file
    file_id = "to_delete.txt"
    content = b"File to be deleted"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Upload the file
        headers = {"X-File-Id": file_id}
        await ac.post("/files", headers=headers, content=content)

        # Delete the file
        response = await ac.delete(f"/files/{file_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify file is deleted
        saved_path = Path(override_settings.base_dir) / file_id
        assert not saved_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_file(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/files/nonexistent.txt")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "does not exist" in response.json()["detail"].lower()
