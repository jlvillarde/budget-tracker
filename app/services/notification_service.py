import json
from typing import List, Optional
from app.utils.file_manager import initialize_user_notifcations_file
from datetime import datetime

class NotificationService:
    @staticmethod
    def get_notifications(user_id: int) -> List[dict]:
        notifications_file = initialize_user_notifcations_file(user_id)
        with notifications_file.open('r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return []

    @staticmethod
    def mark_as_read(user_id: int, notification_index: int) -> Optional[dict]:
        notifications_file = initialize_user_notifcations_file(user_id)
        notifications = NotificationService.get_notifications(user_id)
        if 0 <= notification_index < len(notifications):
            notifications[notification_index]['is_read'] = True
            notifications[notification_index]['read_at'] = datetime.utcnow().isoformat() + 'Z'
            with notifications_file.open('w', encoding='utf-8') as f:
                json.dump(notifications, f, indent=2)
            return notifications[notification_index]
        return None

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        notifications_file = initialize_user_notifcations_file(user_id)
        notifications = NotificationService.get_notifications(user_id)
        count = 0
        for n in notifications:
            if not n.get('is_read', False):
                n['is_read'] = True
                n['read_at'] = datetime.utcnow().isoformat() + 'Z'
                count += 1
        with notifications_file.open('w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2)
        return count
