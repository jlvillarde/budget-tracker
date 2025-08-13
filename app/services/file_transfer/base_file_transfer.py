from abc import ABC, abstractmethod

from fastapi import UploadFile
from app.services.storage.storage_factory import storage_factory
from  fastapi.responses import StreamingResponse


class BaseFileTransfer(ABC):
    def __init__(self):
        self.storage = storage_factory()

    @abstractmethod
    def export_file(self, user_id: int) -> StreamingResponse:
        """
        Export a file for the given user.
        Returns the path or storage key of the exported file.
        """
        pass

    @abstractmethod
    def import_file(self, user_id: int, file: UploadFile) -> None:
        """
        Import a file for the given user.
        'file' can be raw file bytes, text, or structured data.
        """
        pass
