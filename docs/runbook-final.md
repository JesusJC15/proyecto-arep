# Runbook final AREP

## Prerequisitos

- Docker Desktop o motor Docker con `docker compose`
- 4 GB de RAM libres recomendados
- Puertos disponibles:
  - `4173`
  - `8000`
  - `5432`

## Arranque oficial

```bash
docker compose up --build -d
```

## Validaciones rapidas

1. Frontend: abrir `http://localhost:4173`
2. Backend health: abrir `http://localhost:8000/health`
3. Backend readiness: abrir `http://localhost:8000/ready`
4. Estado RAG: abrir `http://localhost:8000/rag/status`
5. Metricas: abrir `http://localhost:8000/metrics`

## Flujo de validacion funcional

1. Ingresar como `ana.patient / demo123`
2. Enviar consulta y ejecutar triage
3. Confirmar recomendacion con score, rank y fuentes
4. Cambiar a `dr.suarez / demo123`
5. Tomar el caso escalado
6. Marcarlo como revisado

## Reconstruir indice RAG

Opcion temporal por entorno:

```bash
docker compose run --rm -e AREP_RAG_FORCE_REINDEX=true backend python scripts/reindex_rag.py
```

Opcion completa de demo limpia:

```bash
docker compose down -v
docker compose up --build -d
```

## Reiniciar datos demo

```bash
docker compose down -v
docker compose up --build -d
```

Tambien puedes usar:

```bash
pwsh ./scripts/demo-reset.ps1
```

## Logs utiles

- Backend:

```bash
docker compose logs -f backend
```

- Frontend:

```bash
docker compose logs -f frontend
```

- Postgres:

```bash
docker compose logs -f postgres
```

## Problemas frecuentes

### `docker compose up` falla por puertos ocupados

- Liberar `4173`, `8000` o `5432`
- O cambiar los puertos publicados en `docker-compose.yml`

### `ready` no responde

- Revisar `docker compose logs backend`
- Confirmar que Postgres este `healthy`
- Verificar que `AREP_DATABASE_URL` apunte a `postgres`

### `rag/status` falla o el indice no existe

- Ejecutar el flujo de reconstruccion del indice
- Confirmar que el volumen `backend_runtime` no este corrupto

### La UI carga pero no inicia sesion

- Confirmar que `http://localhost:8000/auth/login` sea accesible
- Revisar CORS configurado para `http://localhost:4173`

## Apagado

```bash
docker compose down
```
