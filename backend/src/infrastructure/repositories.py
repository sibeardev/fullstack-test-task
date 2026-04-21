from fastapi import HTTPException, status
from sqlalchemy import select

from src.core.config import STORAGE_DIR
from src.infrastructure.db.models import Alert, StoredFile
from src.infrastructure.db.session import async_session_maker


class AlertRepository:
    async def list_alerts(self) -> list[Alert]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Alert).order_by(Alert.created_at.desc())
            )
            return list(result.scalars().all())


class StoredFileRepository:
    async def list_files(self) -> list[StoredFile]:
        async with async_session_maker() as session:
            result = await session.execute(
                select(StoredFile).order_by(StoredFile.created_at.desc())
            )
            return list(result.scalars().all())

    async def get_file(self, file_id: str) -> StoredFile:
        async with async_session_maker() as session:
            file_item = await session.get(StoredFile, file_id)
            if not file_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
                )
            return file_item

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        async with async_session_maker() as session:
            file_item = await session.get(StoredFile, file_id)
            if not file_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
                )
            file_item.title = title
            await session.commit()
            await session.refresh(file_item)
            return file_item

    async def delete_file(self, file_id: str) -> None:
        async with async_session_maker() as session:
            file_item = await session.get(StoredFile, file_id)
            if not file_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
                )
            stored_path = STORAGE_DIR / file_item.stored_name
            if stored_path.exists():
                stored_path.unlink()
            await session.delete(file_item)
            await session.commit()
