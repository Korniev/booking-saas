import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.infra.db.models.booking import Booking
from app.infra.db.models.tenant import Tenant
from app.infra.db.models.user import User
from app.modules.bookings.exceptions import BookingOverlapError, InvalidBookingTimeError
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.schemas import BookingCreate
from app.modules.resources.service import ResourceService


class BookingService:
    def __init__(self, repo: BookingRepository, resources: ResourceService):
        self.repo = repo
        self.resources = resources

    async def create(self, session: AsyncSession, tenant: Tenant, user: User, data: BookingCreate) -> Booking:
        if data.end_at <= data.start_at:
            raise InvalidBookingTimeError("end_at must be after start_at")

        # ensures resource exists + belongs to tenant + active
        resource = await self.resources.get(session, tenant, data.resource_id)

        booking = Booking(
            tenant_id=tenant.id,
            resource_id=resource.id,
            user_id=user.id,
            start_at=data.start_at,
            end_at=data.end_at,
            status="pending",
            notes=data.notes,
        )

        try:
            return await self.repo.create(session, booking)
        except IntegrityError as e:
            msg = str(e).lower()
            if "bookings_no_overlap" in msg or "exclude constraint" in msg:
                raise BookingOverlapError("This time slot is already booked")
            raise

    async def cancel(self, session: AsyncSession, tenant: Tenant, booking_id: uuid.UUID) -> Booking:
        booking = await self.repo.get(session, booking_id, tenant.id)
        if not booking:
            raise NotFoundError("Booking not found")

        booking.status = "cancelled"
        await session.commit()
        await session.refresh(booking)
        return booking