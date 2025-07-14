from .config import settings
from app.core.logger import logger

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

# Base class for all models
class Base(DeclarativeBase):
    pass
    

# Create async engine
def create_engine():
    """Create async database engine"""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Convert sync URL to async URL if needed
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_pre_ping=True,   # Verify connections before use
        pool_recycle=300,     # Recycle connections every 5 minutes
    )
    return engine


# Create engine instance
engine = create_engine()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

# Database initialization
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from ..models import User

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

# Database cleanup
async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")
