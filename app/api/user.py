from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Annotated

from ..core.database import get_db
from ..models.user import User
from ..dto.user_dto import UserCreateDTO
from ..services.user_service import UserService

router = APIRouter(tags=["users"])

UserServiceDep = Annotated[UserService, Depends(UserService)]

@router.post("/user")
async def user_signup(
    request: Request,
    user: UserCreateDTO,
    user_service: UserServiceDep,
    db: AsyncSession = Depends(get_db)
):
    return await user_service.create_user(user, db, request)


@router.get("/user/{user_id}", response_model=dict)
async def get_user_by_id(
    user_id: int,
    user_service: UserServiceDep,
    db: AsyncSession = Depends(get_db)
):
    return await user_service.get_user_by_id(user_id, db)

@router.get("/users", response_model=List[dict])
async def get_users(
    user_service: UserServiceDep,
    db: AsyncSession = Depends(get_db)
):
    return await user_service.get_all_users(db)

