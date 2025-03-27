import hashlib
from unittest import mock

import pytest

from app.utils.helpers import _to_stream


@pytest.mark.asyncio
async def test_save_and_read(local_file_driver, sample_data):
    await local_file_driver.save("file.txt", _to_stream(sample_data))
    chunks = [chunk async for chunk in local_file_driver.read("file.txt")]
    assert b"".join(chunks) == sample_data


@pytest.mark.asyncio
async def test_file_exists_and_delete(local_file_driver):
    await local_file_driver.save("delete.txt", _to_stream(b"to delete"))
    assert await local_file_driver.exists("delete.txt")
    await local_file_driver.delete("delete.txt")
    assert not await local_file_driver.exists("delete.txt")


@pytest.mark.asyncio
async def test_file_size(local_file_driver):
    data = b"123456789"
    await local_file_driver.save("size.txt", _to_stream(data))
    assert await local_file_driver.size("size.txt") == len(data)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "algorithm, hash_fn",
    [
        ("sha256", hashlib.sha256),
        ("sha1", hashlib.sha1),
    ],
)
async def test_file_hash_supported(local_file_driver, algorithm, hash_fn):
    data = b"hash me!"
    await local_file_driver.save("hash.txt", _to_stream(data))
    result = await local_file_driver.hash("hash.txt", algorithm=algorithm)
    assert result == hash_fn(data).hexdigest()


@pytest.mark.asyncio
async def test_file_hash_unsupported_algorithm(local_file_driver):
    await local_file_driver.save("unsupported.txt", _to_stream(b"data"))
    with pytest.raises(ValueError, match="Unsupported hash algorithm"):
        await local_file_driver.hash("unsupported.txt", algorithm="unsupported")


@pytest.mark.asyncio
async def test_validate_base_dir_existing(tmp_path):
    from app.storage.local import LocalFileDriver

    driver = LocalFileDriver(str(tmp_path))
    assert driver.base_dir == str(tmp_path)


@pytest.mark.asyncio
async def test_validate_base_dir_non_existent():
    from app.storage.local import LocalFileDriver

    with pytest.raises(FileNotFoundError):
        LocalFileDriver("/non/existent/path")


@pytest.mark.asyncio
async def test_validate_base_dir_not_a_directory(tmp_path):
    from app.storage.local import LocalFileDriver

    file_path = tmp_path / "file.txt"
    file_path.write_text("not a dir")
    with pytest.raises(NotADirectoryError):
        LocalFileDriver(str(file_path))


@pytest.mark.asyncio
async def test_validate_base_dir_no_write_permission():
    from app.storage.local import LocalFileDriver

    with (
        mock.patch("os.path.exists", return_value=True),
        mock.patch("os.path.isdir", return_value=True),
        mock.patch("os.access", return_value=False),
    ):
        with pytest.raises(PermissionError):
            LocalFileDriver("/any/path")
