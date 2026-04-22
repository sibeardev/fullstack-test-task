from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import STORAGE_DIR
from src.core.exceptions import EntityNotFoundError
from src.infrastructure.db.models import Alert, StoredFile


@dataclass(slots=True)
class BaseRepository:
    session: AsyncSession


class AlertRepository(BaseRepository):
    async def list_alerts(self) -> list[Alert]:
        result = await self.session.execute(
            select(Alert).order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)
        self.session.add(alert)
        await self.session.flush()
        await self.session.refresh(alert)
        return alert


class StoredFileRepository(BaseRepository):
    async def list_files(self) -> list[StoredFile]:
        result = await self.session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_file(self, file: StoredFile) -> StoredFile:
        self.session.add(file)
        await self.session.flush()
        await self.session.refresh(file)
        return file

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self.session.get(StoredFile, file_id)
        if not file_item:
            raise EntityNotFoundError("File not found")
        return file_item

    async def update_file(self, file_id: str, **kwargs: dict[str, Any]) -> StoredFile:
        file_item = await self.session.get(StoredFile, file_id)
        if not file_item:
            raise EntityNotFoundError("File not found")
        for key, value in kwargs.items():
            setattr(file_item, key, value)
        await self.session.flush()
        await self.session.refresh(file_item)
        return file_item

    async def delete_file(self, file_id: str) -> None:
        file_item = await self.session.get(StoredFile, file_id)
        if not file_item:
            raise EntityNotFoundError("File not found")
        stored_path = STORAGE_DIR / file_item.stored_name
        if stored_path.exists():
            stored_path.unlink()
        await self.session.delete(file_item)
        await self.session.flush()
