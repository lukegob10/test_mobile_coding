from abc import ABC, abstractmethod
from typing import Any


class VectorDB(ABC):
    @abstractmethod
    def upsert(self, chunk_id: str, vector: list[float], payload: dict[str, Any]) -> None: ...

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    def ping(self) -> bool: ...
