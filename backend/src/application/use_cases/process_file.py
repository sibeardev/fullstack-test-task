from pathlib import Path

from src.core.config import (
    MAX_UPLOAD_SIZE_MB,
    PROHIBITED_EXTENSIONS,
    STORAGE_DIR,
    VALID_PDF_MIME_TYPES,
)
from src.core.exceptions import EntityNotFoundError
from src.domain.enums import ProcessingStatus, ScanStatus
from src.infrastructure.db.uow import UnitOfWork


async def scan_file_for_threats(file_id: str) -> None:
    async with UnitOfWork() as uow:
        repository = uow.files_repo
        try:
            file_item = await repository.get_file(file_id)
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

        await repository.update_file(
            file_id=file_id,
            processing_status=ProcessingStatus.PROCESSING,
            scan_status=ScanStatus.SUSPICIOUS if reasons else ScanStatus.CLEAN,
            scan_details=", ".join(reasons) if reasons else "no threats found",
            requires_attention=bool(reasons),
        )
        await uow.commit()


async def extract_file_metadata(file_id: str) -> None:
    async with UnitOfWork() as uow:
        repository = uow.files_repo
        try:
            file_item = await repository.get_file(file_id)
        except EntityNotFoundError:
            return

        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            await repository.update_file(
                file_id=file_id,
                processing_status=ProcessingStatus.FAILED,
                scan_status=file_item.scan_status or ScanStatus.FAILED,
                scan_details="stored file not found during metadata extraction",
            )
            await uow.commit()
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

        await repository.update_file(
            file_id=file_id,
            processing_status=ProcessingStatus.PROCESSED,
            metadata_json=metadata,
        )
        await uow.commit()


async def send_file_alert(file_id: str) -> None:
    async with UnitOfWork() as uow:
        file_repository = uow.files_repo
        try:
            file_item = await file_repository.get_file(file_id)
        except EntityNotFoundError:
            return
        alert_repository = uow.alerts_repo
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
        await uow.commit()
