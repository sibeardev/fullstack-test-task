import asyncio
from pathlib import Path

from celery import Celery

from src.core.config import (
    MAX_UPLOAD_SIZE_MB,
    PROHIBITED_EXTENSIONS,
    REDIS_URL,
    STORAGE_DIR,
    VALID_PDF_MIME_TYPES,
)
from src.infrastructure.repositories import AlertRepository, StoredFileRepository

_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


celery_app = Celery("file_tasks", broker=REDIS_URL, backend=REDIS_URL)


async def _scan_file_for_threats(file_id: str) -> None:
    file_item = await StoredFileRepository().get_file(file_id)
    if not file_item:
        return

    reasons: list[str] = []
    extension = Path(file_item.original_name).suffix.lower()

    if extension in PROHIBITED_EXTENSIONS:
        reasons.append(f"suspicious extension {extension}")

    if file_item.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        reasons.append(f"file is larger than {MAX_UPLOAD_SIZE_MB} MB")

    if extension == ".pdf" and file_item.mime_type not in VALID_PDF_MIME_TYPES:
        reasons.append("pdf extension does not match mime type")

    await StoredFileRepository().update_file(
        file_id=file_id,
        processing_status="processing",
        scan_status="suspicious" if reasons else "clean",
        scan_details=", ".join(reasons) if reasons else "no threats found",
        requires_attention=bool(reasons),
    )

    extract_file_metadata.delay(file_id)


async def _extract_file_metadata(file_id: str) -> None:
    file_item = await StoredFileRepository().get_file(file_id)
    if not file_item:
        return

    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        await StoredFileRepository().update_file(
            file_id=file_id,
            processing_status="failed",
            scan_status=file_item.scan_status or "failed",
            scan_details="stored file not found during metadata extraction",
        )
        send_file_alert.delay(file_id)
        return

    metadata = {
        "extension": Path(file_item.original_name).suffix.lower(),
        "size_bytes": file_item.size,
        "mime_type": file_item.mime_type,
    }

    if file_item.mime_type.startswith("text/"):
        content = stored_path.read_text(encoding="utf-8", errors="ignore")
        metadata["line_count"] = len(content.splitlines())
        metadata["char_count"] = len(content)
    elif file_item.mime_type == "application/pdf":
        content = stored_path.read_bytes()
        metadata["approx_page_count"] = max(content.count(b"/Type /Page"), 1)

    await StoredFileRepository().update_file(
        file_id=file_id,
        processing_status="processed",
        metadata_json=metadata,
    )

    send_file_alert.delay(file_id)


async def _send_file_alert(file_id: str) -> None:
    file_item = await StoredFileRepository().get_file(file_id)
    if not file_item:
        return
    alert_repository = AlertRepository()
    if file_item.processing_status == "failed":
        await alert_repository.create_alert(
            file_id=file_id, level="critical", message="File processing failed"
        )
    elif file_item.requires_attention:
        await alert_repository.create_alert(
            file_id=file_id,
            level="warning",
            message=f"File requires attention: {file_item.scan_details}",
        )
    else:
        await alert_repository.create_alert(
            file_id=file_id, level="info", message="File processed successfully"
        )


@celery_app.task
def scan_file_for_threats(file_id: str) -> None:
    run_in_worker_loop(_scan_file_for_threats(file_id))


@celery_app.task
def extract_file_metadata(file_id: str) -> None:
    run_in_worker_loop(_extract_file_metadata(file_id))


@celery_app.task
def send_file_alert(file_id: str) -> None:
    run_in_worker_loop(_send_file_alert(file_id))
