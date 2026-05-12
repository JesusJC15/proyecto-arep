from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from threading import Lock


class RateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._events: dict[tuple[str, str], deque[datetime]] = defaultdict(deque)

    def check(self, scope: str, client_id: str, limit: int, window_seconds: int) -> bool:
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=window_seconds)
        key = (scope, client_id)
        with self._lock:
            queue = self._events[key]
            while queue and queue[0] < window_start:
                queue.popleft()
            if len(queue) >= limit:
                return False
            queue.append(now)
            return True
