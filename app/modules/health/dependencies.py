from functools import lru_cache

from app.modules.health.repository import HealthRepository
from app.modules.health.service import HealthService


@lru_cache
def get_health_repo() -> HealthRepository:
    return HealthRepository()


@lru_cache
def get_health_service() -> HealthService:
    return HealthService(repo=get_health_repo())