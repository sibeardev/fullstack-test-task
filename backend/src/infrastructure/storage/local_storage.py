from pathlib import Path

from src.core.config import STORAGE_DIR
from src.core.exceptions import EntityNotFoundError
from src.infrastructure.db.models import StoredFile
from src.infrastructure.db.uow import UnitOfWork


async def get_file_path(file_id: str) -> tuple[StoredFile, Path]:
    async with UnitOfWork() as uow:
        file_item = await uow.files_repo.get_file(file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise EntityNotFoundError("Stored file not found")
    return file_item, stored_path
