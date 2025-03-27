from typing import Annotated

from fastapi import Depends

from app.deps.storage import DriverDep
from app.services.file_service import FileService


def get_file_service(driver: DriverDep) -> FileService:
    return FileService(driver=driver)


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
