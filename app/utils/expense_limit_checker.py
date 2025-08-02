import json
from datetime import datetime
from app.utils.file_manager import initialize_user_settings_file, initialize_user_notifcations_file

class ExpenseLimitChecker:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.settings_file = initialize_user_settings_file(user_id)
        self.notifications_file = initialize_user_notifcations_file(user_id)
        self.settings = self._load_settings()

    def _load_settings(self):
        with self.settings_file.open('r', encoding='utf-8') as f:
            return json.load(f)

    def _add_notification(self, detail: str, title: str, date_str: str):
        # Load or create notifications file
        try:
            with self.notifications_file.open('r', encoding='utf-8') as f:
                notifications = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            notifications = []
        notif_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{len(notifications)+1}"
        notification = {
            'id': notif_id,
            'title': title,
            'detail': detail,
            'is_read': False,
            'date': date_str
        }
        notifications.append(notification)
        with self.notifications_file.open('w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2)

    def check_and_notify(self, total_today: float, total_week: float, total_month: float):
        limits = self.settings.get('budgetLimits', {})
        exceeded_details = []
        # Load notifications for duplicate check
        try:
            with self.notifications_file.open('r', encoding='utf-8') as f:
                notifications = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            notifications = []
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        week_str = datetime.utcnow().strftime('%Y-W%U')
        month_str = datetime.utcnow().strftime('%Y-%m')
        # Check daily limit
        daily_limit = limits.get('daily', 0)
        if daily_limit and daily_limit > 0 and total_today > daily_limit:
            if not any(n['title'] == 'Daily Limit' and n.get('date') == today_str for n in notifications):
                detail = f"You have exceeded your daily expense limit of {daily_limit}."
                self._add_notification(detail, "Daily Limit", today_str)
                exceeded_details.append({
                    "title": "Daily Limit",
                    "detail": detail,
                    "date": today_str
                })
        # Check weekly limit
        weekly_limit = limits.get('weekly', 0)
        if weekly_limit and weekly_limit > 0 and total_week > weekly_limit:
            if not any(n['title'] == 'Weekly Limit' and n.get('date') == week_str for n in notifications):
                detail = f"You have exceeded your weekly expense limit of {weekly_limit}."
                self._add_notification(detail, "Weekly Limit", week_str)
                exceeded_details.append({
                    "title": "Weekly Limit",
                    "detail": detail,
                    "date": week_str
                })
        # Check monthly limit
        monthly_limit = limits.get('monthly', 0)
        if monthly_limit and monthly_limit > 0 and total_month > monthly_limit:
            if not any(n['title'] == 'Monthly Limit' and n.get('date') == month_str for n in notifications):
                detail = f"You have exceeded your monthly expense limit of {monthly_limit}."
                self._add_notification(detail, "Monthly Limit", month_str)
                exceeded_details.append({
                    "title": "Monthly Limit",
                    "detail": detail,
                    "date": month_str
                })
        return exceeded_details
