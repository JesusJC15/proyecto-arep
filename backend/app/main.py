from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.logging import log_event, request_id_ctx
from app.core.metrics import MetricsCollector
from app.core.rate_limit import RateLimiter
from app.core.settings import Settings, load_settings
from app.repositories.sql_repository import SQLRepository
from app.services.rag_service import RAGService


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        app.state.store.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()
    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
        summary="Plataforma academica de triaje medico con RAG y trazabilidad",
        lifespan=app_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    store = SQLRepository(resolved_settings.database_url)
    store.initialize(seed_demo_data=resolved_settings.seed_demo_data)
    rag_service = RAGService(store=store, settings=resolved_settings)
    rag_service.initialize(force_reindex=resolved_settings.rag_force_reindex)
    app.state.settings = resolved_settings
    app.state.store = store
    app.state.rag_service = rag_service
    app.state.metrics = MetricsCollector()
    app.state.rate_limiter = RateLimiter()

    app.include_router(api_router)

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        request_id = request.headers.get(resolved_settings.request_id_header, str(uuid4()))
        token = request_id_ctx.set(request_id)
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((perf_counter() - started) * 1000, 3)
            app.state.metrics.record_request(request.method, request.url.path, 500, duration_ms)
            log_event(
                "http.request",
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
                outcome="error",
                error_type=type(exc).__name__,
            )
            request_id_ctx.reset(token)
            raise
        duration_ms = round((perf_counter() - started) * 1000, 3)
        app.state.metrics.record_request(request.method, request.url.path, response.status_code, duration_ms)
        response.headers[resolved_settings.request_id_header] = request_id
        log_event(
            "http.request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            outcome="success" if response.status_code < 400 else "failure",
        )
        request_id_ctx.reset(token)
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        log_event(
            "http.exception",
            path=request.url.path,
            method=request.method,
            error_type=type(exc).__name__,
            detail=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id_ctx.get(),
            },
        )

    @app.get("/", tags=["meta"])
    def read_root() -> dict[str, str]:
        return {
            "project": resolved_settings.app_name,
            "status": "ready",
            "docs": "/docs",
            "database_backend": "sqlite" if resolved_settings.database_url.startswith("sqlite:///") else "postgresql",
        }

    return app


app = create_app()
