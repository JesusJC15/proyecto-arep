# Runbook Final AREP

Runbook operativo para la entrega final de AREP. Define como arrancar, verificar, observar y reiniciar la demo oficial.

## Sistema oficial

- Frontend: http://localhost:4173
- Backend health: http://localhost:8000/health
- Backend ready: http://localhost:8000/ready
- RAG status: http://localhost:8000/rag/status
- Metrics: http://localhost:8000/metrics

## Arranque

```bash
docker compose up --build -d
```

Verificacion rapida:

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

## Credenciales demo

- `ana.patient` / `demo123`
- `dr.suarez` / `demo123`

## Flujo de validacion

1. Abrir el frontend.
2. Iniciar sesion como paciente.
3. Crear una consulta y ejecutar triage.
4. Confirmar que la recomendacion muestra evidencia, score y trazabilidad.
5. Iniciar sesion como profesional.
6. Abrir la bandeja de casos, asignar el caso y marcarlo como revisado.

## Operacion diaria

- Si el frontend no responde, revisar el contenedor `arep-frontend`.
- Si el backend no responde, revisar `arep-backend` y la cadena de conexion a Postgres.
- Si `GET /ready` falla, revisar primero `docker compose ps` y despues `docker compose logs -f backend`.
- Si `GET /rag/status` falla, revisar `artifacts/rag-index.json` y la inicializacion del servicio RAG.

## Reset de demo

```bash
pwsh ./scripts/demo-reset.ps1
```

Equivalente en shell:

```bash
bash ./scripts/demo-reset.sh
```

## Escenarios de error frecuentes

- Puertos ocupados: cerrar procesos en 4173, 8000 o 5432.
- Credenciales invalidas: verificar rol y usuario exacto.
- CORS: revisar `AREP_CORS_ORIGINS`.
- Persistencia vacia: confirmar que `AREP_SEED_DEMO_DATA=true`.

## Criterio de aceptacion

- El frontend abre.
- El backend responde.
- La base de datos esta saludable.
- El RAG devuelve estado listo.
- La demo de paciente y profesional se completa sin errores manuales.