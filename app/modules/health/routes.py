from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import db_session
from app.modules.health.dependencies import get_health_service
from app.modules.health.service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/db")
async def health_db(
    session: AsyncSession = Depends(db_session),
    service: HealthService = Depends(get_health_service),
):
    db_value = await service.check_db(session)
    return {"db": db_value}