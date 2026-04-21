import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from src.core.config import DEFAULT_MIME_TYPE, STORAGE_DIR
from src.infrastructure.db.models import StoredFile
from src.infrastructure.db.session import async_session_maker
from src.infrastructure.repositories import StoredFileRepository


async def create_file(title: str, upload_file: UploadFile) -> StoredFile:
    content = await upload_file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty"
        )

    file_id = str(uuid4())
    suffix = Path(upload_file.filename or "").suffix
    stored_name = f"{file_id}{suffix}"
    stored_path = STORAGE_DIR / stored_name
    stored_path.write_bytes(content)

    file_item = StoredFile(
        id=file_id,
        title=title,
        original_name=upload_file.filename or stored_name,
        stored_name=stored_name,
        mime_type=upload_file.content_type
        or mimetypes.guess_type(stored_name)[0]
        or DEFAULT_MIME_TYPE,
        size=len(content),
        processing_status="uploaded",
    )
    async with async_session_maker() as session:
        session.add(file_item)
        await session.commit()
        await session.refresh(file_item)
    return file_item


async def get_file_path(file_id: str) -> tuple[StoredFile, Path]:
    file_item = await StoredFileRepository().get_file(file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )
    return file_item, stored_path
