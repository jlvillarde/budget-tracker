import json
from typing import List, Optional
from app.utils.file_manager import initialize_user_notifcations_file
from datetime import datetime
from app.services.storage.storage_factory import storage_factory

class NotificationService:
    def __init__(self):
        self.storage = storage_factory()

    def _read_notifications(self, user_id: int) -> list:
        """Read notifications for a user from the configured storage."""
        notifications = storage_factory().load_file(user_id, 'notifications')
        return notifications if isinstance(notifications, list) else [notifications]
    
    def _write_notifications(self, user_id: int, data: list):
        """Save notification into notifications file"""
        return self.storage.save_file(user_id, 'notifications', data)

    def get_notifications(self, user_id: int) -> list:
        notifications = self._read_notifications(user_id)
        return notifications
    
    def mark_all_as_read(self, user_id: int) -> int:
        notifications = self._read_notifications(user_id)
        count = 0
        for n in notifications:
            if not n.get('is_read', False):
                n['is_read'] = True
                n['read_at'] = datetime.utcnow().isoformat() + 'Z'
                count += 1

        self.storage.save_file(user_id, 'notifications', notifications)
        return count
