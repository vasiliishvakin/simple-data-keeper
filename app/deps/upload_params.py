from typing import Annotated, Optional

from fastapi import Depends, Header, Query

from app.schemas.file_params import FileUploadParams


def get_upload_params(
    file_id: Annotated[str, Header(alias="X-File-Id")],
    hash: Annotated[Optional[str], Header(alias="X-File-Hash")] = None,
    algorithm: Annotated[Optional[str], Header(alias="X-File-Hash-Algorithm")] = None,
    background: Annotated[bool, Query()] = False,
) -> FileUploadParams:
    return FileUploadParams(
        file_id=file_id,
        hash=hash,
        algorithm=algorithm,
        background=background,
    )


UploadParamsDep = Annotated[FileUploadParams, Depends(get_upload_params)]
