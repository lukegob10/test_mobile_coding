import time
from collections import Counter
from typing import Any

from backend.app.core.settings import get_settings
from backend.app.ingest.embed import embed_text
from backend.app.rag.validators import validate_citations, validate_top_k
from backend.app.repository import Repository
from backend.app.vectordb.base import VectorDB


class ReactAgent:
    def __init__(self, repo: Repository, vectordb: VectorDB) -> None:
        self.repo = repo
        self.vectordb = vectordb

    def run(self, collection_id: str, query: str, top_k: int, filters: dict[str, Any] | None = None, include_trace: bool = False) -> dict:
        settings = get_settings()
        validate_top_k(top_k, settings.max_top_k)
        t0 = time.perf_counter()
        trace = []
        used_chunk_ids: set[str] = set()

        action = {'tool': 'vector_search', 'args': {'query': query, 'top_k': top_k, 'filters': {'collection_id': collection_id, **(filters or {})}}}
        results = self.vectordb.search(embed_text(query), top_k=top_k, filters=action['args']['filters'])
        trace.append({'type': 'action', 'data': action})
        trace.append({'type': 'observation', 'data': results})

        chunk_obs = []
        for row in results[: min(top_k, settings.max_iters)]:
            chunk = self.repo.get_chunk(row['chunk_id'])
            if chunk:
                used_chunk_ids.add(chunk.chunk_id)
                obs = {
                    'chunk_id': chunk.chunk_id,
                    'doc_id': chunk.doc_id,
                    'filename': chunk.filename,
                    'chunk_index': chunk.chunk_index,
                    'text': chunk.text[:1200],
                }
                chunk_obs.append(obs)
                trace.append({'type': 'action', 'data': {'tool': 'get_chunk', 'args': {'chunk_id': chunk.chunk_id}}})
                trace.append({'type': 'observation', 'data': obs})

        answer, citations, confidence = _compose_answer(query, chunk_obs)
        citations = validate_citations(citations, used_chunk_ids)
        if not citations:
            answer = 'Insufficient evidence found in retrieved documents. Please upload/add more relevant docs or refine your query.'
            confidence = 'low'

        final = {'answer': answer, 'citations': citations, 'confidence': confidence}
        trace.append({'type': 'final', 'data': final})
        out = {**final, 'timings': {'total_ms': round((time.perf_counter() - t0) * 1000, 2)}}
        if include_trace:
            out['trace'] = trace
        return out


def _compose_answer(query: str, chunks: list[dict]) -> tuple[str, list[dict], str]:
    if not chunks:
        return '', [], 'low'
    q_words = [w for w in query.lower().split() if len(w) > 2]
    scored = []
    for c in chunks:
        text_l = c['text'].lower()
        score = sum(1 for w in q_words if w in text_l)
        scored.append((score, c))
    scored.sort(reverse=True, key=lambda x: x[0])
    best = [c for s, c in scored if s > 0][:3]
    if not best:
        return '', [], 'low'

    sentences = []
    citations = []
    for c in best:
        first = c['text'].split('\n')[0][:220]
        sentences.append(first)
        citations.append({'doc_id': c['doc_id'], 'filename': c['filename'], 'chunk_id': c['chunk_id'], 'chunk_index': c['chunk_index']})

    confidence = 'high' if len(best) >= 2 else 'med'
    return ' '.join(sentences), citations, confidence
