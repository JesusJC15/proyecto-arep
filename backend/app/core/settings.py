from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "AREP Triage MVP"
    app_version: str = "0.4.0"
    environment: str = "development"
    database_url: str = "sqlite:///data/arep_demo.sqlite3"
    jwt_secret: str = "arep-insecure-development-secret"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60
    seed_demo_data: bool = True
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    )
    request_id_header: str = "X-Request-ID"
    auth_rate_limit_count: int = 5
    auth_rate_limit_window_seconds: int = 60
    mutation_rate_limit_count: int = 20
    mutation_rate_limit_window_seconds: int = 60
    enable_metrics: bool = True
    rag_embedding_provider: str = "local"
    rag_embedding_model: str = "hashed-tfidf-v1"
    rag_embedding_api_url: str | None = None
    rag_embedding_api_key: str | None = None
    rag_chunk_size: int = 90
    rag_chunk_overlap: int = 18
    rag_top_k: int = 3
    rag_index_artifact_path: str = "artifacts/rag-index.json"
    rag_corpus_version: str = "2026-05-phase3"
    rag_force_reindex: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"prod", "production"}


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    return int(value)


def load_settings() -> Settings:
    cors_raw = os.getenv("AREP_CORS_ORIGINS")
    cors_origins = Settings.cors_origins if not cors_raw else tuple(
        origin.strip() for origin in cors_raw.split(",") if origin.strip()
    )
    settings = Settings(
        environment=os.getenv("AREP_ENV", Settings.environment),
        database_url=os.getenv("AREP_DATABASE_URL", Settings.database_url),
        jwt_secret=os.getenv("AREP_JWT_SECRET", Settings.jwt_secret),
        jwt_algorithm=os.getenv("AREP_JWT_ALGORITHM", Settings.jwt_algorithm),
        access_token_ttl_minutes=_parse_int(
            os.getenv("AREP_ACCESS_TOKEN_TTL_MINUTES"),
            Settings.access_token_ttl_minutes,
        ),
        seed_demo_data=_parse_bool(os.getenv("AREP_SEED_DEMO_DATA"), Settings.seed_demo_data),
        cors_origins=cors_origins,
        request_id_header=os.getenv("AREP_REQUEST_ID_HEADER", Settings.request_id_header),
        auth_rate_limit_count=_parse_int(
            os.getenv("AREP_AUTH_RATE_LIMIT_COUNT"),
            Settings.auth_rate_limit_count,
        ),
        auth_rate_limit_window_seconds=_parse_int(
            os.getenv("AREP_AUTH_RATE_LIMIT_WINDOW_SECONDS"),
            Settings.auth_rate_limit_window_seconds,
        ),
        mutation_rate_limit_count=_parse_int(
            os.getenv("AREP_MUTATION_RATE_LIMIT_COUNT"),
            Settings.mutation_rate_limit_count,
        ),
        mutation_rate_limit_window_seconds=_parse_int(
            os.getenv("AREP_MUTATION_RATE_LIMIT_WINDOW_SECONDS"),
            Settings.mutation_rate_limit_window_seconds,
        ),
        enable_metrics=_parse_bool(os.getenv("AREP_ENABLE_METRICS"), Settings.enable_metrics),
        rag_embedding_provider=os.getenv("AREP_RAG_EMBEDDING_PROVIDER", Settings.rag_embedding_provider),
        rag_embedding_model=os.getenv("AREP_RAG_EMBEDDING_MODEL", Settings.rag_embedding_model),
        rag_embedding_api_url=os.getenv("AREP_RAG_EMBEDDING_API_URL"),
        rag_embedding_api_key=os.getenv("AREP_RAG_EMBEDDING_API_KEY"),
        rag_chunk_size=_parse_int(os.getenv("AREP_RAG_CHUNK_SIZE"), Settings.rag_chunk_size),
        rag_chunk_overlap=_parse_int(os.getenv("AREP_RAG_CHUNK_OVERLAP"), Settings.rag_chunk_overlap),
        rag_top_k=_parse_int(os.getenv("AREP_RAG_TOP_K"), Settings.rag_top_k),
        rag_index_artifact_path=os.getenv("AREP_RAG_INDEX_ARTIFACT_PATH", Settings.rag_index_artifact_path),
        rag_corpus_version=os.getenv("AREP_RAG_CORPUS_VERSION", Settings.rag_corpus_version),
        rag_force_reindex=_parse_bool(os.getenv("AREP_RAG_FORCE_REINDEX"), Settings.rag_force_reindex),
    )
    validate_settings(settings)
    return settings


def validate_settings(settings: Settings) -> None:
    if settings.access_token_ttl_minutes <= 0:
        raise ValueError("AREP_ACCESS_TOKEN_TTL_MINUTES must be greater than zero")
    if settings.auth_rate_limit_count <= 0 or settings.auth_rate_limit_window_seconds <= 0:
        raise ValueError("Auth rate limit configuration must be positive")
    if settings.mutation_rate_limit_count <= 0 or settings.mutation_rate_limit_window_seconds <= 0:
        raise ValueError("Mutation rate limit configuration must be positive")
    if not settings.database_url.startswith(("sqlite:///", "postgresql+psycopg://")):
        raise ValueError("AREP_DATABASE_URL must use sqlite:/// or postgresql+psycopg://")
    if settings.rag_embedding_provider not in {"local", "external_openai_compatible"}:
        raise ValueError("AREP_RAG_EMBEDDING_PROVIDER must be local or external_openai_compatible")
    if settings.rag_chunk_size <= 0:
        raise ValueError("AREP_RAG_CHUNK_SIZE must be greater than zero")
    if settings.rag_chunk_overlap < 0 or settings.rag_chunk_overlap >= settings.rag_chunk_size:
        raise ValueError("AREP_RAG_CHUNK_OVERLAP must be between 0 and chunk size - 1")
    if settings.rag_top_k <= 0:
        raise ValueError("AREP_RAG_TOP_K must be greater than zero")
    if settings.rag_embedding_provider == "external_openai_compatible":
        if not settings.rag_embedding_api_url or not settings.rag_embedding_api_key:
            raise ValueError(
                "AREP_RAG_EMBEDDING_API_URL and AREP_RAG_EMBEDDING_API_KEY are required for external embeddings"
            )
    if settings.is_production and settings.jwt_secret == Settings.jwt_secret:
        raise ValueError("AREP_JWT_SECRET must be overridden outside development")
