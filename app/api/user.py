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

@router.post("/signup")
async def user_signup(
    request: Request,
    user: UserCreateDTO,
    user_service: UserServiceDep,
    db: AsyncSession = Depends(get_db)
):
    return await user_service.create_user(user, db, request)


# @router.get("/user/{user_id}", response_model=dict)
# async def get_user_by_id(
#     user_id: int,
#     user_service: UserServiceDep,
#     db: AsyncSession = Depends(get_db)
# ):
#     return await user_service.get_user_by_id(user_id, db)

@router.get("/user/me")
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_session = request.session.get("user")
    if not user_session or "id" not in user_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user_session["id"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Return user data (excluding sensitive info like password)
    return {
        "id": user.id,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

@router.get("/users", response_model=List[dict])
async def get_users(
    user_service: UserServiceDep,
    db: AsyncSession = Depends(get_db)
):
    return await user_service.get_all_users(db)

