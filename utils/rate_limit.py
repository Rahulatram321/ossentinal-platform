"""Small in-process rate limiter for interactive AI endpoints.

For multi-worker production deployments replace this with Redis; keeping the
interface here makes that migration contained and preserves safe defaults.
"""
from collections import defaultdict, deque
from time import monotonic

_hits: dict[str, deque[float]] = defaultdict(deque)


def allowed(key: str, limit: int, period_seconds: int = 3600) -> bool:
    now = monotonic()
    window = _hits[key]
    while window and window[0] <= now - period_seconds:
        window.popleft()
    if len(window) >= limit:
        return False
    window.append(now)
    return True
