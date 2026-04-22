from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.session import async_session_maker
from src.infrastructure.repositories import AlertRepository, StoredFileRepository


class UnitOfWork:
    def __init__(self) -> None:
        self.session: AsyncSession | None = None
        self.files: StoredFileRepository | None = None
        self.alerts: AlertRepository | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = async_session_maker()
        self.files = StoredFileRepository(self.session)
        self.alerts = AlertRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return
        if exc_type is not None:
            await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        if self.session is None:
            return
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            return
        await self.session.rollback()

    @property
    def files_repo(self) -> StoredFileRepository:
        if self.files is None:
            raise RuntimeError("UnitOfWork is not initialized")
        return self.files

    @property
    def alerts_repo(self) -> AlertRepository:
        if self.alerts is None:
            raise RuntimeError("UnitOfWork is not initialized")
        return self.alerts
