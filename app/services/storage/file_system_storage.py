import json
from app.services.storage.storage_base import FileStorage
from app.utils.file_manager import get_user_dir
from app.core.logger import logger


class FileSystemStorage(FileStorage):
    def save_file(self, user_id: int, filename: str, data) -> bool:
        """
        If `data` is dict -> append to existing list.
        If `data` is list -> replace file content.
        """
        try:
            user_directory = get_user_dir(user_id)
            user_directory.mkdir(parents=True, exist_ok=True)
            file_path = user_directory / filename

            if isinstance(data, list):
                # replace file
                with file_path.open("w", encoding="utf-8") as file:
                    json.dump(data, file, indent=2)
                return True

            # append
            if file_path.exists():
                with file_path.open("r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []

            if not isinstance(existing_data, list):
                existing_data = [existing_data] if existing_data else []

            existing_data.append(data)

            with file_path.open("w", encoding="utf-8") as file:
                json.dump(existing_data, file, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error saving file {filename} for user {user_id}: {e}")
            return False

    def load_file(self, user_id: int, filename: str) -> list:
        try:
            file_path = get_user_dir(user_id) / filename
            if not file_path.exists():
                return []
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"Error loading file {filename} for user {user_id}: {e}")
            return []
