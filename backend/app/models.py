from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Collection:
    id: str
    name: str
    config: dict = field(default_factory=dict)


@dataclass
class Document:
    doc_id: str
    collection_id: str
    filename: str
    sha256: str
    storage_path: str
    created_at: datetime


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    collection_id: str
    filename: str
    chunk_index: int
    text: str
