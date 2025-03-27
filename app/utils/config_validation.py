import os
from pathlib import Path

from app.config import settings
from app.storage.enums import StorageDriverType


def validate_files_local_base_dir(base_dir: str) -> str:
    abs_path = str(Path(base_dir).resolve())

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Storage base_dir does not exist: {abs_path}")

    if not os.path.isdir(abs_path):
        raise NotADirectoryError(f"Storage base_dir is not a directory: {abs_path}")

    if not os.access(abs_path, os.W_OK):
        raise PermissionError(f"No write permission for base_dir: {abs_path}")

    return abs_path


def validate_storage_driver():
    if settings.storage_driver not in StorageDriverType._value2member_map_:
        raise ValueError(f"Unsupported storage driver: {settings.storage_driver}. Valid options: {[driver.value for driver in StorageDriverType]}")
