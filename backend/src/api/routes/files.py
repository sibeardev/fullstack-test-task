from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from src.api.schemas.files import FileItem, FileUpdate
from src.application.use_cases.upload_file import create_file
from src.core.exceptions import EntityNotFoundError
from src.infrastructure.db.session import async_session_maker
from src.infrastructure.repositories import StoredFileRepository
from src.infrastructure.storage.local_storage import get_file_path
from src.workers.tasks import scan_file_for_threats_task

TITLE_FORM_PARAM = Form(...)
UPLOAD_FILE_PARAM = File(...)

files_router = APIRouter(prefix="/files", tags=["files"])


@files_router.get("", response_model=list[FileItem])
async def list_files_view():
    async with async_session_maker() as session:
        return await StoredFileRepository(session).list_files()


@files_router.post("", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = TITLE_FORM_PARAM,
    file: UploadFile = UPLOAD_FILE_PARAM,
):
    file_item = await create_file(title=title, upload_file=file)
    scan_file_for_threats_task.delay(file_item.id)
    return file_item


@files_router.get("/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str):
    try:
        async with async_session_maker() as session:
            return await StoredFileRepository(session).get_file(file_id)
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        ) from exc


@files_router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
):
    try:
        async with async_session_maker() as session:
            return await StoredFileRepository(session).update_file(
                file_id=file_id, title=payload.title
            )
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        ) from exc


@files_router.get("/{file_id}/download")
async def download_file(file_id: str):
    stored_file, stored_path = await get_file_path(file_id)
    return FileResponse(
        path=stored_path,
        media_type=stored_file.mime_type,
        filename=stored_file.original_name,
    )


@files_router.delete("/{file_id}", status_code=204)
async def delete_file_view(file_id: str):
    try:
        async with async_session_maker() as session:
            await StoredFileRepository(session).delete_file(file_id)
    except EntityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        ) from exc
