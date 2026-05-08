from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter

from app.core.logging import log_event


@contextmanager
def trace_span(name: str, **fields):
    start = perf_counter()
    log_event("trace.start", span=name, **fields)
    try:
        yield
    finally:
        duration_ms = round((perf_counter() - start) * 1000, 3)
        log_event("trace.end", span=name, duration_ms=duration_ms, **fields)
