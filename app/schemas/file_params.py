from typing import Optional

from pydantic import BaseModel, model_validator


class FileUploadParams(BaseModel):
    file_id: str
    hash: Optional[str] = None
    algorithm: Optional[str] = None
    background: bool = False

    @model_validator(mode="after")
    def check_hash_and_algorithm(self) -> "FileUploadParams":
        if bool(self.hash) != bool(self.algorithm):
            raise ValueError("Both 'hash' and 'algorithm' must be provided together or both omitted.")
        return self
