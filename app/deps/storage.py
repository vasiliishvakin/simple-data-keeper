from typing import Annotated

from fastapi import Depends

from app.deps.settings import SettingsDep
from app.storage.base import StorageDriver
from app.storage.enums import StorageDriverType
from app.storage.local import LocalFileDriver


def get_storage_driver(settings: SettingsDep) -> StorageDriver:
    match settings.storage_driver:
        case StorageDriverType.LOCAL:
            return LocalFileDriver(base_dir=settings.base_dir)
        case _:
            raise ValueError(f"Unsupported storage driver: {settings.storage_driver}")


DriverDep = Annotated[StorageDriver, Depends(get_storage_driver)]
