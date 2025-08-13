from enum import StrEnum

from app.services.file_transfer.base_file_transfer import BaseFileTransfer
from app.services.file_transfer.csv_file_transfer import CsvFileTransfer


class FileType(StrEnum):
    CSV = 'csv'
    JSON  = 'json'

def file_transfer_factory(file_type: FileType) -> BaseFileTransfer:
    if file_type == FileType.CSV:
        return CsvFileTransfer()
    else:
        return CsvFileTransfer()