import json
from app.utils.file_manager import initialize_user_settings_file
from app.services.storage.storage_factory import storage_factory

class SettingsService:

    def __init__(self):
        self.storage = storage_factory()

    def _read_settings(self, user_id: int) -> list:
        """Read settings for a user from the configured storage."""
        notifications = storage_factory().load_file(user_id, 'settings')
        return notifications if isinstance(notifications, list) else [notifications]
    
    def _write_settings(self, user_id: int, data: list):
        """Save setting into settings file"""
        return self.storage.save_file(user_id, 'settings', data)


    def get_user_settings(self, user_id: int) -> list:
        settings = self._read_settings(user_id)
        return settings[0]
    
    def update_user_settings(self, user_id: int, updated_settings: dict) -> dict:
        self.storage.save_file(user_id, 'settings', [updated_settings])
        return updated_settings
