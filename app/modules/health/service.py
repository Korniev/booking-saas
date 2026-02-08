from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.health.repository import HealthRepository


class HealthService:
    def __init__(self, repo: HealthRepository):
        self.repo = repo

    async def check_db(self, session: AsyncSession) -> int:
        return await self.repo.check_db(session)