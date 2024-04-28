import os
import uuid


def generate_file_path(ext: str) -> str:
    return os.path.join('app', 'static', f'{uuid.uuid4()}{ext}')
