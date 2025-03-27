from pathlib import Path
from typing import AsyncIterator

import pytest
from fastapi import FastAPI

from app.config.settings import Settings
from app.deps.settings import get_settings
from app.main import create_app
from app.services.file_service import FileService
from app.storage.local import LocalFileDriver
from app.utils.helpers import _to_stream


@pytest.fixture
def local_file_driver(tmp_path: Path) -> LocalFileDriver:
    return LocalFileDriver(base_dir=str(tmp_path), default_chunk_size=4)


@pytest.fixture
def sample_data() -> bytes:
    return b"Hello, world!"


@pytest.fixture
def sample_stream(sample_data: bytes) -> AsyncIterator[bytes]:
    return _to_stream(sample_data)


@pytest.fixture
def file_service(local_file_driver: LocalFileDriver) -> FileService:
    return FileService(driver=local_file_driver)


@pytest.fixture
def override_settings(tmp_path: Path) -> Settings:
    return Settings(debug=True, base_dir=str(tmp_path))


@pytest.fixture
def app(override_settings: Settings) -> FastAPI:
    app = create_app(override_settings)
    app.dependency_overrides[get_settings] = lambda: override_settings
    yield app
    app.dependency_overrides.clear()
