from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.logger import logger
from ..models.user import User
from ..dto.user_dto import UserCreateDTO
from ..utils.hash_util import hash_password

class UserService:

    async def create_user(
        self,
        user: UserCreateDTO,
        db: AsyncSession,
        request: Request 
    ):
        try:
            """Create a new user (simplified - no password hashing for demo)"""
            # Check if user already exists
            existing_user = await db.execute(
                select(User).where(
                    (User.email == user.email)
                )
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Create new user (in production, hash the password!)
            new_user = User(
                email=user.email,
                password=hash_password(user.password),
                firstname=user.firstname,
                lastname=user.lastname
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            request.session['user'] = {
                "id": new_user.id,
                "email": new_user.email
            }

            return RedirectResponse(
                url='/dashboard',
                status_code=303
            )
        except HTTPException as httpexc:
            logger.warning(httpexc)
            raise
        except Exception as exc:
            logger.error(exc)


    async def get_user_by_id(
        self,
        user_id: int,
        db: AsyncSession
    ):
        try:
            """Get a specific user by ID"""
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {
                "id": user.id,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        
        except HTTPException as httpexc:
            logger.warning(httpexc)
            raise
        except Exception as exc:
            logger.error(exc)
            

    async def get_all_users(
        self,
        db: AsyncSession
    ):
        try:
            """Get all users"""
            result = await db.execute(select(User))
            users = result.scalars().all()
            return [
                {
                    "id": user.id,
                    "email": user.email,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "is_active": user.is_active,
                    "created_at": user.created_at
                }
                for user in users
            ]

        except HTTPException as httpexc:
            logger.warning(httpexc)
            raise
        except Exception as exc:
            logger.error(exc)