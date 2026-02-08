from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthRepository:
    async def check_db(self, session: AsyncSession) -> int:
        result = await session.execute(text("SELECT 1"))
        return result.scalar_one()