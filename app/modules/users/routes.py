from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import db_session
from app.infra.db.models.user import User
from app.modules.auth.dependencies import require_active_user, require_superuser
from app.modules.users.dependencies import get_user_service
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead)
async def register_user(
    payload: UserCreate,
    session: AsyncSession = Depends(db_session),
    service: UserService = Depends(get_user_service),
):
    return await service.register(session, payload)


@router.get("/me", response_model=UserRead)
async def read_me(user: User = Depends(require_active_user)):
    return user


@router.get("", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db_session),
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_superuser),
):
    return await service.list_users(session, skip=skip, limit=limit)