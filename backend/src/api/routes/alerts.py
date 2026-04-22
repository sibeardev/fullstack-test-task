from fastapi import APIRouter

from src.api.schemas.alerts import AlertItem
from src.infrastructure.db.uow import UnitOfWork

alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


@alerts_router.get("", response_model=list[AlertItem])
async def list_alerts_view():
    async with UnitOfWork() as uow:
        return await uow.alerts_repo.list_alerts()
