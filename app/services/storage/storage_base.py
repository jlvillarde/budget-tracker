from abc import ABC, abstractmethod

class FileStorage(ABC):

    @abstractmethod
    def save_file(self, user_id: int, filename: str, data: list[dict]) -> bool:
        pass

    @abstractmethod
    def load_file(self, user_id: int, filename: str) -> list:
        pass