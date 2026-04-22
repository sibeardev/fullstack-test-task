import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from src.core.config import DEFAULT_MIME_TYPE, STORAGE_DIR
from src.domain.enums import ProcessingStatus
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

    async with async_session_maker() as session:
        file_item = await StoredFileRepository(session).create_file(
            StoredFile(
                id=file_id,
                title=title,
                original_name=upload_file.filename or stored_name,
                stored_name=stored_name,
                mime_type=upload_file.content_type
                or mimetypes.guess_type(stored_name)[0]
                or DEFAULT_MIME_TYPE,
                size=len(content),
                processing_status=ProcessingStatus.UPLOADED,
            )
        )
    return file_item
