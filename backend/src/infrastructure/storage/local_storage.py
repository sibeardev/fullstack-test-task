from pathlib import Path

from fastapi import HTTPException, status

from src.core.config import STORAGE_DIR
from src.core.exceptions import EntityNotFoundError
from src.infrastructure.db.models import StoredFile
from src.infrastructure.repositories import StoredFileRepository


async def get_file_path(file_id: str) -> tuple[StoredFile, Path]:
    try:
        file_item = await StoredFileRepository().get_file(file_id)
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        ) from exc
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )
    return file_item, stored_path
