from sqlalchemy import select

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
