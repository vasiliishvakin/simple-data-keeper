from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response, StreamingResponse

from app.deps.services import FileServiceDep
from app.deps.upload_params import UploadParamsDep
from app.utils.helpers import _to_stream

router = APIRouter()


@router.post("/files", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, response_model=None)
async def upload_file(
    request: Request,
    upload_params: UploadParamsDep,
    file_service: FileServiceDep,
) -> Response:
    stream = request.stream()

    try:
        if upload_params.hash and upload_params.algorithm:
            await file_service.save_file_with_hash_check(
                file_id=upload_params.file_id,
                stream=stream,
                expected_hash=upload_params.hash,
                algorithm=upload_params.algorithm,
            )
        elif upload_params.background:
            content = await request.body()
            await file_service.save_file_background(
                file_id=upload_params.file_id,
                stream=_to_stream(content),
            )
        else:
            await file_service.save_file(file_id=upload_params.file_id, stream=stream)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/files/{file_id}", response_class=StreamingResponse)
async def get_file(
    file_id: str,
    file_service: FileServiceDep,
) -> StreamingResponse:
    # Check if file exists before attempting to stream
    if not await file_service.check_file_exists(file_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{file_id}' not found")

    file_data = await file_service.get_file(file_id)
    return StreamingResponse(
        content=file_data["content"],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_data["filename"]}"'},
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_file(
    file_id: str,
    file_service: FileServiceDep,
) -> Response:
    try:
        await file_service.delete_file_checked(file_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
