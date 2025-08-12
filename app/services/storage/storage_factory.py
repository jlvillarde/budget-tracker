from app.services.storage.file_system_storage import FileSystemStorage
from app.services.storage.storage_base import FileStorage
from app.services.storage.supabase_storage import SupabaseStorage
from app.core.config import settings


def storage_factory() -> FileStorage:
    """
    Factory function to create the appropriate storage instance based on configuration.
    """
    if settings.APP_ENV == "production":
        return SupabaseStorage()
    else:
        return FileSystemStorage()  # Default to file system storage





