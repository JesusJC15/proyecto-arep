# Backend Fase 4

Backend FastAPI para AREP. Implementa JWT firmado, password hashing, repositorio SQL compatible con SQLite/Postgres, auditoria persistida, rate limiting basico, metricas, `rag/status` y empaquetado listo para Docker Compose.

## Endpoints

- `POST /auth/login`
- `GET /auth/session`
- `POST /consultations`
- `GET /consultations/{id}`
- `POST /consultations/{id}/triage`
- `GET /consultations/{id}/recommendation`
- `GET /professional/cases`
- `GET /professional/cases/{id}`
- `POST /professional/cases/{id}/assign`
- `POST /professional/cases/{id}/review`
- `GET /rag/status`
- `GET /health`
- `GET /ready`
- `GET /metrics`

## Ejecucion esperada

```bash
docker compose up --build -d
```

## Configuracion

Variables soportadas:

- `AREP_ENV`
- `AREP_DATABASE_URL`
- `AREP_JWT_SECRET`
- `AREP_JWT_ALGORITHM`
- `AREP_ACCESS_TOKEN_TTL_MINUTES`
- `AREP_SEED_DEMO_DATA`
- `AREP_CORS_ORIGINS` (incluye puertos de Vite y Playwright segun necesidad)
- `AREP_REQUEST_ID_HEADER`
- `AREP_AUTH_RATE_LIMIT_COUNT`
- `AREP_AUTH_RATE_LIMIT_WINDOW_SECONDS`
- `AREP_MUTATION_RATE_LIMIT_COUNT`
- `AREP_MUTATION_RATE_LIMIT_WINDOW_SECONDS`
- `AREP_ENABLE_METRICS`
- `AREP_RAG_EMBEDDING_PROVIDER`
- `AREP_RAG_EMBEDDING_MODEL`
- `AREP_RAG_EMBEDDING_API_URL`
- `AREP_RAG_EMBEDDING_API_KEY`
- `AREP_RAG_CHUNK_SIZE`
- `AREP_RAG_CHUNK_OVERLAP`
- `AREP_RAG_TOP_K`
- `AREP_RAG_INDEX_ARTIFACT_PATH`
- `AREP_RAG_CORPUS_VERSION`
- `AREP_RAG_FORCE_REINDEX`

Ver `./.env.example` para un ejemplo minimo.

Para validar compatibilidad Postgres en pruebas, definir `TEST_POSTGRES_URL` con un DSN `postgresql+psycopg://...`.

## Usuarios demo

- `ana.patient` / `demo123`
- `dr.suarez` / `demo123`

## Validacion

```bash
python -m pytest -q
```

## Operacion

- Runbook: [../docs/runbook-final.md](../docs/runbook-final.md)
- Compose oficial: [../docker-compose.yml](../docker-compose.yml)
- Dockerfile: [Dockerfile](Dockerfile)

## Evaluacion RAG

- Dataset minimo en `../knowledge-base/evaluation/rag-evaluation-dataset.json`
- Metricas actuales del dataset de referencia:
  - `top-1 hit`: `2/3`
  - `top-k hit`: `3/3`

## Nota

La seguridad y el retrieval siguen siendo de alcance academico. Esta fase deja una API reproducible y demostrable, no una plataforma clinica productiva.
