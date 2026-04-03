from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 120, per_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith(("/health", "/ready")):
            return await call_next(request)

        key = request.client.host if request.client else "unknown"
        now = time.time()
        window = self._requests[key]

        while window and now - window[0] > self.per_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": str(self.per_seconds)},
            )

        window.append(now)
        return await call_next(request)
