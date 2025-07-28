import json
from app.utils.file_manager import initialize_user_settings_file

class SettingsService:
    def get_user_settings(self, user_id: int) -> dict:
        settings_file = initialize_user_settings_file(user_id)
        with settings_file.open("r", encoding="utf-8") as f:
            data =  json.load(f)
        # print(data['budgetLimits'])
        return data
    

    def update_user_settings(self, user_id: int, updated_settings: dict) -> dict:
        settings_file = initialize_user_settings_file(user_id)
        # Write new settings
        with settings_file.open("w", encoding="utf-8") as f:
            json.dump(updated_settings, f, indent=2)
        return updated_settings
