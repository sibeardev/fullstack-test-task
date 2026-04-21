from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from src.api.schemas.files import FileItem, FileUpdate
from src.core.config import STORAGE_DIR
from src.infrastructure.repositories import StoredFileRepository
from src.service import create_file, delete_file
from src.workers.tasks import scan_file_for_threats

files_router = APIRouter(prefix="/files", tags=["files"])


@files_router.get("", response_model=list[FileItem])
async def list_files_view():
    return await StoredFileRepository().list_files()


@files_router.post("", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
):
    file_item = await create_file(title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@files_router.get("/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str):
    return await StoredFileRepository().get_file(file_id)


@files_router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
):
    return await StoredFileRepository().update_file(file_id=file_id, title=payload.title)


@files_router.get("/{file_id}/download")
async def download_file(file_id: str):
    file_item = await StoredFileRepository().get_file(file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@files_router.delete("/{file_id}", status_code=204)
async def delete_file_view(file_id: str):
    await delete_file(file_id)
