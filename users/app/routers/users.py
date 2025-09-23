from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db_session
from .. import models
from ..schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_db_session)):
    res = await session.execute(select(models.User).order_by(models.User.id))
    return [UserRead.model_validate(u) for u in res.scalars().all()]

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_db_session)):
    # Check for duplicate email (simple approach for now)
    exists = await session.scalar(select(models.User).where(models.User.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = models.User(email=payload.email, name=payload.name)
    session.add(user)
    await session.flush()  # obtain autoincremented id
    return UserRead.model_validate(user)