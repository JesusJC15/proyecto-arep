from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse

from app.dependencies import get_rag_service
from app.services.rag_service import RAGService
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


@router.get("/rag/source", tags=["meta"], response_class=PlainTextResponse)
def rag_source(
    uri: str = Query(..., min_length=1),
    rag_service: RAGService = Depends(get_rag_service),
) -> PlainTextResponse:
    content = rag_service.read_source_content(uri)
    return PlainTextResponse(content=content, media_type="text/markdown")
