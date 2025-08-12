import json
from supabase import create_client
from app.services.storage.storage_base import FileStorage
from app.core import config
from app.core.logger import logger


class SupabaseStorage(FileStorage):
    def __init__(self):
        self.url = config.settings.SUPABASE_URL
        self.key = config.settings.SUPABASE_KEY
        self.bucket = config.settings.SUPABASE_BUCKET_NAME

        if not self.url or not self.key:
            logger.warning("Supabase URL/KEY not set. SupabaseStorage will fail until they are configured.")

        self.client = create_client(self.url, self.key)

    def _load_file_data(self, path: str):
        try:
            data = self.client.storage.from_(self.bucket).download(path)

            # Return empty list if no data
            if data is None:
                return []
            
            # Normalize the downloaded file into a bytes object.
            if isinstance(data, memoryview):
                raw_bytes = data.tobytes()
            elif isinstance(data, (bytes, bytearray)):
                raw_bytes = bytes(data)
            else:
                try:
                    raw_bytes = data.read()
                except:
                    raw_bytes = bytes(data)

            if not raw_bytes:
                return []
        
            # Convert bytes into dict/list
            return json.loads(raw_bytes.decode('utf-8'))
        
        except Exception as e:
            logger.debug(f"Supabase download error for '{path}': {e}")
            return []

    def _download_json(self, path: str):
        try:
            result = self.client.storage.from_(self.bucket).download(path)
            if result is None:
                return []

            if isinstance(result, memoryview):
                raw_bytes = result.tobytes()
            elif isinstance(result, (bytes, bytearray)):
                raw_bytes = bytes(result)
            else:
                try:
                    raw_bytes = result.read()
                except AttributeError:
                    raw_bytes = bytes(result)

            if not raw_bytes:
                return []

            return json.loads(raw_bytes.decode("utf-8"))
        except Exception as e:
            logger.debug(f"Supabase download error for '{path}': {e}")
            return []

    def _upload_json(self, path: str, data) -> bool:
        try:
            content = json.dumps(data, indent=2).encode("utf-8")
            try:
                self.client.storage.from_(self.bucket).upload(
                    path, content, file_options={"content-type": "application/json", "upsert": "true"}
                )
            except TypeError:
                self.client.storage.from_(self.bucket).upload(path, content)
            return True
        except Exception as e:
            logger.error(f"Supabase upload error for '{path}': {e}")
            return False

    def save_file(self, user_id: int, filename: str, data) -> bool:
        """
        If `data` is dict -> append to existing list.
        If `data` is list -> replace file content.
        """
        try:
            file_path = f"user_{user_id}/{filename}"

            if isinstance(data, list):
                # replace entire file
                return self._upload_json(file_path, data)

            # otherwise append
            existing = self._download_json(file_path)
            if not isinstance(existing, list):
                existing = [] if not existing else [existing]
            existing.append(data)
            return self._upload_json(file_path, existing)

        except Exception as e:
            logger.error(f"Error saving file {filename} for user {user_id}: {e}")
            return False

    def load_file(self, user_id: int, filename: str) -> list[dict]:
        try:
            file_path = f"user_{user_id}/{filename}"
            result = self._download_json(file_path)
            if isinstance(result, list):
                return result
            if result == [] or result is None:
                return []
            return [result]
        except Exception as e:
            logger.error(f"Error loading file {filename} for user {user_id}: {e}")
            return []
