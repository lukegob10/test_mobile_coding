import json
import logging
import time
from collections.abc import Callable

from fastapi import Request, Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'time': int(time.time() * 1000),
        }
        if hasattr(record, 'request_id'):
            payload['request_id'] = record.request_id
        return json.dumps(payload)


def configure_logging(level: str) -> None:
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logging.getLogger('app.request').info(
        f'{request.method} {request.url.path} -> {response.status_code} ({elapsed_ms:.2f}ms)'
    )
    return response
