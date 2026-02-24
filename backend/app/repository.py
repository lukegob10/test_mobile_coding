import hashlib
from datetime import datetime
from uuid import uuid4

from backend.app.models import Chunk, Collection, Document


class Repository:
    def __init__(self) -> None:
        self.collections: dict[str, Collection] = {}
        self.documents: dict[str, Document] = {}
        self.chunks: dict[str, Chunk] = {}

    def create_collection(self, name: str, config: dict | None = None) -> Collection:
        col = Collection(id=str(uuid4()), name=name, config=config or {})
        self.collections[col.id] = col
        return col

    def delete_collection(self, collection_id: str) -> None:
        self.collections.pop(collection_id, None)
        for doc in [d.doc_id for d in self.documents.values() if d.collection_id == collection_id]:
            self.delete_document(doc)

    def list_collections(self) -> list[Collection]:
        return list(self.collections.values())

    def add_document(self, collection_id: str, filename: str, sha256: str, storage_path: str) -> Document:
        doc = Document(str(uuid4()), collection_id, filename, sha256, storage_path, datetime.utcnow())
        self.documents[doc.doc_id] = doc
        return doc

    def find_doc_by_sha(self, collection_id: str, sha256: str) -> Document | None:
        for d in self.documents.values():
            if d.collection_id == collection_id and d.sha256 == sha256:
                return d
        return None

    def list_documents(self, collection_id: str) -> list[Document]:
        return [d for d in self.documents.values() if d.collection_id == collection_id]

    def delete_document(self, doc_id: str) -> None:
        self.documents.pop(doc_id, None)
        for chunk_id in [c.chunk_id for c in self.chunks.values() if c.doc_id == doc_id]:
            self.chunks.pop(chunk_id, None)

    def add_chunk(self, doc_id: str, collection_id: str, filename: str, chunk_index: int, text: str) -> Chunk:
        chunk = Chunk(str(uuid4()), doc_id, collection_id, filename, chunk_index, text)
        self.chunks[chunk.chunk_id] = chunk
        return chunk

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        return self.chunks.get(chunk_id)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
