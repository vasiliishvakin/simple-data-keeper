import re
from hashlib import sha256

import pytest

from app.utils.helpers import _to_stream


@pytest.mark.asyncio
async def test_save_and_get_file(file_service, sample_data):
    file_id = "testfile"
    await file_service.save_file(file_id, _to_stream(sample_data))
    result = await file_service.get_file(file_id)

    content = b""
    async for chunk in result["content"]:
        content += chunk

    assert result["filename"] == file_id
    assert content == sample_data


@pytest.mark.asyncio
async def test_read_file_fully(file_service, sample_data):
    file_id = "fullread"
    await file_service.save_file(file_id, _to_stream(sample_data))
    result = await file_service.read_file_fully(file_id)
    assert result == sample_data


@pytest.mark.asyncio
async def test_check_file_exists(file_service, sample_data):
    file_id = "existfile"
    await file_service.save_file(file_id, _to_stream(sample_data))
    assert await file_service.check_file_exists(file_id) is True


@pytest.mark.asyncio
async def test_delete_file(file_service, sample_data):
    file_id = "deletefile"
    await file_service.save_file(file_id, _to_stream(sample_data))
    await file_service.delete_file(file_id)
    assert not await file_service.check_file_exists(file_id)


@pytest.mark.asyncio
async def test_delete_file_checked_success(file_service, sample_data):
    file_id = "todelete"
    await file_service.save_file(file_id, _to_stream(sample_data))
    await file_service.delete_file_checked(file_id)
    assert not await file_service.check_file_exists(file_id)


@pytest.mark.asyncio
async def test_delete_file_checked_fail(file_service):
    file_id = "notfound"
    await file_service.delete_file(file_id)

    with pytest.raises(RuntimeError, match=re.compile(r"does not exist before deletion|was not deleted")):
        await file_service.delete_file_checked(file_id)


@pytest.mark.asyncio
async def test_get_file_size(file_service, sample_data):
    file_id = "sizefile"
    await file_service.save_file(file_id, _to_stream(sample_data))
    size = await file_service.get_file_size(file_id)
    assert size == len(sample_data)


@pytest.mark.asyncio
async def test_get_file_hash(file_service, sample_data):
    file_id = "hashfile"
    await file_service.save_file(file_id, _to_stream(sample_data))
    expected = sha256(sample_data).hexdigest()
    actual = await file_service.get_file_hash(file_id, "sha256")
    assert actual == expected


@pytest.mark.asyncio
async def test_save_file_with_hash_check_success(file_service, sample_data):
    file_id = "hashcheck"
    hash_val = sha256(sample_data).hexdigest()
    await file_service.save_file_with_hash_check(file_id, _to_stream(sample_data), hash_val, "sha256")


@pytest.mark.asyncio
async def test_save_file_with_hash_check_failure(file_service, sample_data):
    file_id = "hashfail"
    wrong_hash = "0000"
    with pytest.raises(ValueError, match="Hash mismatch"):
        await file_service.save_file_with_hash_check(file_id, _to_stream(sample_data), wrong_hash, "sha256")
