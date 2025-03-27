from pathlib import Path
from typing import AsyncIterator


def safe_join(base_dir: str, relative_path: str) -> str:
    base = Path(base_dir).resolve()
    target = (base / relative_path).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError("Path escapes base directory")

    return str(target)


async def _to_stream(data: bytes) -> AsyncIterator[bytes]:
    yield data
