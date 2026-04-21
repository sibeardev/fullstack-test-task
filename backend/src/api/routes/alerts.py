from fastapi import APIRouter

from src.api.schemas.alerts import AlertItem
from src.infrastructure.repositories import AlertRepository

alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])


@alerts_router.get("", response_model=list[AlertItem])
async def list_alerts_view():
    return await AlertRepository().list_alerts()
