from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..core.database import get_db
from ..models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[dict])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Get all users"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
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
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "bio": user.bio,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.post("/", response_model=dict)
async def create_user(
    email: str,
    username: str,
    password: str,
    full_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user (simplified - no password hashing for demo)"""
    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(
            (User.email == email) | (User.username == username)
        )
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user (in production, hash the password!)
    new_user = User(
        email=email,
        username=username,
        hashed_password=password,  # In production, use proper password hashing
        full_name=full_name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "created_at": new_user.created_at
    } 