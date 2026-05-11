# Runbook final AREP

## Prerequisitos

- Docker Desktop o motor Docker con `docker compose`
- 4 GB de RAM libres recomendados
- Puertos disponibles: 4173, 8000, 5432

## Arranque oficial

```bash
docker compose up --build -d
```

## Validaciones rapidas

1. Frontend: `http://localhost:4173`
2. Backend health: `http://localhost:8000/health`
3. Backend readiness: `http://localhost:8000/ready`
4. Estado RAG: `http://localhost:8000/rag/status`
