import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    # Application settings
    APP_NAME: str = "FastAPI React App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Environment
    APP_ENV  = os.getenv("APP_ENV", "development").lower()

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Security settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-secret-key-change-in-production")
    SESSION_SECRET_KEY: str = os.getenv(
        'SESSION_SECRET_KEY', "session_secret_key")
    
    # Database url
    DATABASE_URL: str | None = os.getenv("DATABASE_URL", None)

    # Supabase Storage settings
    SUPABASE_URL: str = str(os.getenv("SUPABASE_URL", None))
    SUPABASE_KEY: str = str(os.getenv("SUPABASE_KEY", None))
    SUPABASE_BUCKET_NAME: str = str(os.getenv("SUPABASE_BUCKET_NAME", "user-files"))    

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "detailed")

    # CORS settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
    ]

    # File paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    STATIC_DIR: Path = BASE_DIR / "app" / "static"
    LOGS_DIR: Path = BASE_DIR / "logs"

    @classmethod
    def get_cors_origins(cls) -> list:
        """Get CORS origins from environment or use defaults"""
        origins = os.getenv("CORS_ORIGINS")
        if origins:
            return [origin.strip() for origin in origins.split(",")]
        return cls.ALLOWED_ORIGINS


# Create settings instance
settings = Settings()
