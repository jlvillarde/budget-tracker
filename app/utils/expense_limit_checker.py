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
        exceeded = False
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
            # Only notify if not already notified for today
            if not any(n['title'] == 'Daily Limit' and n.get('date') == today_str for n in notifications):
                self._add_notification(
                    f"You have exceeded your daily expense limit of {daily_limit}.",
                    title="Daily Limit",
                    date_str=today_str
                )
            exceeded = True
        # Check weekly limit
        weekly_limit = limits.get('weekly', 0)
        if weekly_limit and weekly_limit > 0 and total_week > weekly_limit:
            # Only notify if not already notified for this week
            if not any(n['title'] == 'Weekly Limit' and n.get('date') == week_str for n in notifications):
                self._add_notification(
                    f"You have exceeded your weekly expense limit of {weekly_limit}.",
                    title="Weekly Limit",
                    date_str=week_str
                )
            exceeded = True
        # Check monthly limit
        monthly_limit = limits.get('monthly', 0)
        if monthly_limit and monthly_limit > 0 and total_month > monthly_limit:
            # Only notify if not already notified for this month
            if not any(n['title'] == 'Monthly Limit' and n.get('date') == month_str for n in notifications):
                self._add_notification(
                    f"You have exceeded your monthly expense limit of {monthly_limit}.",
                    title="Monthly Limit",
                    date_str=month_str
                )
            exceeded = True
        return exceeded
