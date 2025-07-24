from typing import Optional
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, select

from app.utils.hash_util import verify_password
from ..core.logger import logger
from ..models.user import User
from ..dto.user_dto import UserCreateDTO
from ..utils.hash_util import verify_password


class AuthService:

    async def login(
        self,
        email: str,
        password: str,
        db: AsyncSession,
        request: Request
    ):
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=400, detail='Invalid password or email')

        match_password = verify_password(password, user.password)
        if not match_password:
            raise HTTPException(status_code=400, detail='Invalid password or email')

        request.session['user'] = {
            "id": user.id,
            "email": user.email
        }

    
        return JSONResponse(
            content={
                "id": user.id,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "is_active": user.is_active,
                "updated_at": user.updated_at
            },
            status_code=200
        )

    async def logout(self, request: Request):
        request.session.clear()
        return JSONResponse(
            content={"message": "Logout successful"},
            status_code=200
        )