import os
import uuid


class FileSize:
    GB = 1024*1024*1024*1024
    MB = 1024*1024*1024
    KB = 1024*1024

    @staticmethod
    def get_gb(b: int):
        return b / FileSize.GB

    @staticmethod
    def get_mb(b: int):
        return b / FileSize.MB

    @staticmethod
    def get_kb(b: int):
        return b / FileSize.KB


def generate_file_path(ext: str) -> str:
    return os.path.join('app', 'static', f'{uuid.uuid4()}{ext}')


def delete_file(file_path: str):
    if file_exists(file_path):
        os.remove(file_path)


def file_exists(file_path: str):
    return os.path.exists(file_path)
