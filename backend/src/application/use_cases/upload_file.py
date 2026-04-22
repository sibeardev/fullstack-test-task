import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from src.core.config import DEFAULT_MIME_TYPE, STORAGE_DIR
from src.core.exceptions import ValidationError
from src.domain.enums import ProcessingStatus
from src.infrastructure.db.models import StoredFile
from src.infrastructure.db.uow import UnitOfWork

CHUNK_SIZE = 1024 * 1024


async def create_file(title: str, upload_file: UploadFile) -> StoredFile:
    file_id = str(uuid4())
    suffix = Path(upload_file.filename or "").suffix
    stored_name = f"{file_id}{suffix}"
    stored_path = STORAGE_DIR / stored_name

    size = 0
    with stored_path.open("wb") as file_obj:
        while True:
            chunk = await upload_file.read(CHUNK_SIZE)
            if not chunk:
                break
            file_obj.write(chunk)
            size += len(chunk)

    if size == 0:
        if stored_path.exists():
            stored_path.unlink()
        raise ValidationError("File is empty")

    async with UnitOfWork() as uow:
        file_item = await uow.files_repo.create_file(
            StoredFile(
                id=file_id,
                title=title,
                original_name=upload_file.filename or stored_name,
                stored_name=stored_name,
                mime_type=upload_file.content_type
                or mimetypes.guess_type(stored_name)[0]
                or DEFAULT_MIME_TYPE,
                size=size,
                processing_status=ProcessingStatus.UPLOADED,
            )
        )
        await uow.commit()
    return file_item
