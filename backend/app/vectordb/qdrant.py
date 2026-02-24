import math
from typing import Any

from backend.app.vectordb.base import VectorDB


class InMemoryVectorDB(VectorDB):
    def __init__(self) -> None:
        self.rows: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def upsert(self, chunk_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        self.rows[chunk_id] = (vector, payload)

    def search(self, query_vector: list[float], top_k: int, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        scored: list[dict[str, Any]] = []
        for chunk_id, (vec, payload) in self.rows.items():
            if any(payload.get(k) != v for k, v in filters.items()):
                continue
            score = _cosine(query_vector, vec)
            scored.append({'chunk_id': chunk_id, 'score': score, **payload})
        return sorted(scored, key=lambda x: x['score'], reverse=True)[:top_k]

    def ping(self) -> bool:
        return True


def _cosine(a: list[float], b: list[float]) -> float:
    denom = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
    if not denom:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / denom
