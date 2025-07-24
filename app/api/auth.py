from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import APIRouter, Depends, Request

from app.dto.auth_dto import LoginDTO
from ..services.auth_service import AuthService
from ..core.database import get_db

router = APIRouter(tags=['authentication'])

AuthServiceDep = Annotated[AuthService, Depends(AuthService)]

@router.post('/login')
async def login(
    login_dto: LoginDTO,
    auth_service: AuthServiceDep,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.login(login_dto.email, login_dto.password, db, request)

@router.post('/logout')
async def logout(
    auth_service: AuthServiceDep,
    request: Request,
):
    return await auth_service.logout(request)