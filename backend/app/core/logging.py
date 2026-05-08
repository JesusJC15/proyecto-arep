from __future__ import annotations

from contextvars import ContextVar
from datetime import UTC, datetime
import json
import logging
from typing import Any


request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("arep")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


logger = configure_logging()


def log_event(event: str, level: int = logging.INFO, **fields: Any) -> None:
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        "request_id": request_id_ctx.get(),
        **fields,
    }
    logger.log(level, json.dumps(payload, default=str, ensure_ascii=True))
