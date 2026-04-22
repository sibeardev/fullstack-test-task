from fastapi import APIRouter

from src.api.schemas.alerts import AlertItem
from src.infrastructure.db.session import async_session_maker
from src.infrastructure.repositories import AlertRepository

alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


@alerts_router.get("", response_model=list[AlertItem])
async def list_alerts_view():
    async with async_session_maker() as session:
        return await AlertRepository(session).list_alerts()
