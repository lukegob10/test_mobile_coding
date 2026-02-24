import json
import uuid
from collections.abc import Generator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.app.core.auth import require_api_key
from backend.app.core.rate_limit import rag_rate_limit
from backend.app.deps import agent

router = APIRouter(prefix='/react', tags=['react'], dependencies=[Depends(require_api_key), Depends(rag_rate_limit)])


class ReactQuery(BaseModel):
    collection_id: str
    query: str
    top_k: int = 6
    filters: dict | None = None
    stream: bool = False
    include_trace: bool = False


@router.post('/query')
def react_query(payload: ReactQuery):
    request_id = str(uuid.uuid4())
    result = agent.run(payload.collection_id, payload.query, payload.top_k, payload.filters, payload.include_trace)
    result['request_id'] = request_id
    return result


@router.get('/stream')
def react_stream(collection_id: str, query: str, top_k: int = 6, include_trace: bool = False):
    request_id = str(uuid.uuid4())

    def generate() -> Generator[str, None, None]:
        result = agent.run(collection_id, query, top_k, None, include_trace=True)
        for step in result.get('trace', []):
            yield f"event: step\ndata: {json.dumps(step)}\n\n"
        final = {k: v for k, v in result.items() if k != 'trace'}
        final['request_id'] = request_id
        if include_trace:
            final['trace'] = result.get('trace', [])
        yield f"event: final\ndata: {json.dumps(final)}\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')
