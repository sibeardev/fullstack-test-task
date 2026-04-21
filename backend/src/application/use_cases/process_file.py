from pathlib import Path

from src.core.config import (
    MAX_UPLOAD_SIZE_MB,
    PROHIBITED_EXTENSIONS,
    STORAGE_DIR,
    VALID_PDF_MIME_TYPES,
)
from src.core.exceptions import EntityNotFoundError
from src.domain.enums import ProcessingStatus
from src.infrastructure.repositories import AlertRepository, StoredFileRepository


async def scan_file_for_threats(file_id: str) -> None:
    try:
        file_item = await StoredFileRepository().get_file(file_id)
    except EntityNotFoundError:
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
        processing_status=ProcessingStatus.PROCESSING,
        scan_status="suspicious" if reasons else "clean",
        scan_details=", ".join(reasons) if reasons else "no threats found",
        requires_attention=bool(reasons),
    )


async def extract_file_metadata(file_id: str) -> None:
    try:
        file_item = await StoredFileRepository().get_file(file_id)
    except EntityNotFoundError:
        return

    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        await StoredFileRepository().update_file(
            file_id=file_id,
            processing_status=ProcessingStatus.FAILED,
            scan_status=file_item.scan_status or "failed",
            scan_details="stored file not found during metadata extraction",
        )
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
        processing_status=ProcessingStatus.PROCESSED,
        metadata_json=metadata,
    )


async def send_file_alert(file_id: str) -> None:
    try:
        file_item = await StoredFileRepository().get_file(file_id)
    except EntityNotFoundError:
        return
    alert_repository = AlertRepository()
    if file_item.processing_status == ProcessingStatus.FAILED:
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
