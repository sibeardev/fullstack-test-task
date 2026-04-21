from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette import status

from src.api.routes.alerts import alerts_router
from src.api.schemas.files import FileItem, FileUpdate
from src.core.config import STORAGE_DIR, settings
from src.service import (
    create_file,
    delete_file,
    get_file,
    list_files,
    update_file,
)
from src.workers.tasks import scan_file_for_threats

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS.ALLOW_ORIGINS,
    allow_credentials=settings.CORS.ALLOW_CREDENTIALS,
    allow_methods=settings.CORS.ALLOW_METHODS,
    allow_headers=settings.CORS.ALLOW_HEADERS,
)

app.include_router(alerts_router)


@app.get("/files", response_model=list[FileItem])
async def list_files_view():
    return await list_files()


@app.post("/files", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
):
    file_item = await create_file(title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@app.get("/files/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str):
    return await get_file(file_id)


@app.patch("/files/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
):
    return await update_file(file_id=file_id, title=payload.title)


@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    file_item = await get_file(file_id)
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


@app.delete("/files/{file_id}", status_code=204)
async def delete_file_view(file_id: str):
    await delete_file(file_id)
