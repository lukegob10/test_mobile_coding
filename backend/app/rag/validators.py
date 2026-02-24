from fastapi import HTTPException


def validate_top_k(top_k: int, max_top_k: int) -> None:
    if top_k < 1 or top_k > max_top_k:
        raise HTTPException(status_code=422, detail=f'top_k must be 1..{max_top_k}')


def validate_citations(citations: list[dict], allowed_chunk_ids: set[str]) -> list[dict]:
    return [c for c in citations if c.get('chunk_id') in allowed_chunk_ids]
