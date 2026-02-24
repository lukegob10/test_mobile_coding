import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from backend.app.core.settings import get_settings


class SimpleRateLimiter:
    def __init__(self) -> None:
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int) -> None:
        now = time.time()
        window = 60.0
        q = self.hits[key]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='Rate limit exceeded')
        q.append(now)


rate_limiter = SimpleRateLimiter()


async def rag_rate_limit(request: Request) -> None:
    client = request.client.host if request.client else 'unknown'
    rate_limiter.check(client, get_settings().rate_limit_per_minute)
