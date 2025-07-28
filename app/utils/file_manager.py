from pathlib import Path
import json

def get_user_dir(user_id: int):
    user_dir = Path("data") / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def initialize_user_expenses_file(user_id: int):
    user_data_dir = get_user_dir(user_id)
    file_path = user_data_dir / 'expenses.json'

    if not file_path.exists():
        with file_path.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    return file_path

def initialize_user_notifcations_file(user_id: int):
    user_data_dir = get_user_dir(user_id)
    file_path = user_data_dir / 'notifications.json'

    if not file_path.exists():
        with file_path.open("w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    return file_path

def initialize_user_categories_file(user_id: int):
    user_data_dir = get_user_dir(user_id)
    file_path = user_data_dir / 'categories.json'

    if not file_path.exists():
        default_categories = [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Personal Care",
        ]
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(default_categories, f, indent=2)

    return file_path

def initialize_user_settings_file(user_id: int):
    user_data_dir = get_user_dir(user_id)
    file_path = user_data_dir / 'settings.json'

    if not file_path.exists():
        default_data = {
            'budgetLimits': {
                'daily': 0,
                'weekly': 0,
                'monthly': 0,
        }
        }
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)

    return file_path
