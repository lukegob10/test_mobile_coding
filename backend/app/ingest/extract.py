from pathlib import Path


ALLOWED_SUFFIXES = {'.txt', '.md', '.html', '.htm'}


def extract_text(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix and suffix not in ALLOWED_SUFFIXES:
        raise ValueError('Unsupported file type for MVP')
    return data.decode('utf-8', errors='ignore')
