from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.schemas.domain import RAGStatus

router = APIRouter()


@router.get("/health", tags=["meta"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", tags=["meta"])
def readiness(request: Request) -> dict[str, str]:
    request.app.state.store.healthcheck()
    request.app.state.rag_service.get_status()
    return {"status": "ready"}


@router.get("/metrics", tags=["meta"], response_class=PlainTextResponse)
def metrics(request: Request) -> str:
    return request.app.state.metrics.render_prometheus()


@router.get("/rag/status", tags=["meta"], response_model=RAGStatus)
def rag_status(request: Request) -> RAGStatus:
    return request.app.state.rag_service.get_status()
