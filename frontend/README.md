# Frontend Fase 4

Cliente React para la base preproductiva ligera AREP. Presenta tres espacios:

- Portal del paciente conectado a la API real.
- Espacio profesional con bandeja real de casos.
- Vista estatica de arquitectura para apoyo de presentacion.
- Suite E2E con Playwright para el flujo principal.
- Evidencia RAG visible con score, ranking, metodo y razon de recuperacion.
- Empaquetado para Docker Compose como frontend oficial de demo.

## Scripts esperados

```bash
docker compose up --build -d
```

## Configuracion

Definir `VITE_API_BASE_URL` si la API no corre en `http://127.0.0.1:8000`.

## E2E

```bash
npx playwright install chromium
npm run test:e2e
```

## Nota

El flujo principal usa backend real con JWT, auditoria, persistencia SQL y retrieval semantico local. La vista de arquitectura sigue siendo estatica para apoyar la demo y la presentacion academica.

Artefactos principales:

- Compose oficial: [../docker-compose.yml](../docker-compose.yml)
- Dockerfile: [Dockerfile](Dockerfile)
- Slides HTML: [../docs/presentation/index.html](../docs/presentation/index.html)
