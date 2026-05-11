# AREP — Entrega final profesional

AREP es una plataforma académica de triaje médico asistido por IA, diseñada para demostrar un flujo completo: captura de síntomas, evaluación asistida por reglas y modelos, recuperación semántica (RAG) con trazabilidad y roles (paciente/profesional). Este repositorio contiene la demo completa, la infraestructura de ejemplo, la documentación académica y los artefactos para presentación.

## Qué incluye

- Frontend: aplicación React (canal paciente y canal profesional) con visualización de evidencia, scores y trazabilidad.
- Backend: API en FastAPI con autenticación JWT, control de roles, auditoría, métricas y endpoints RAG (`/rag/status`).
- Base de datos: Postgres configurada para la demo.
- Knowledge-base: corpus y procesos de evaluación RAG y scripts reproducibles para indexado.
- Infraestructura de ejemplo: plantillas y notas para desplegar en AWS (blueprint y diagramas).
- Material académico: paper, slides y documentación de respaldo para sustentación.

## Arquitectura resumida

- `frontend`: React + Vite, bundle estático listo para hosting estático (S3/CloudFront).
- `backend`: FastAPI con dependencias, servicios de triage, repositorios y endpoints REST.
- `postgres`: persistencia relacional para usuarios y eventos de auditoría.
- `knowledge-base`: corpus y pipelines para construir índices RAG (vectores, metadatos).
- `artifacts`: índices y datos reproducibles para evaluación.

## Demo desplegada

La interfaz frontend está desplegada en AWS (hosting estático S3 public) y accesible públicamente en:

- https://arep-production-frontend.s3-website-us-east-1.amazonaws.com/

Nota: el backend en este repositorio está preparado para despliegue (ver `infra/aws`) y puede ejecutarse localmente con Docker Compose.

## Arranque rápido (local)

1. Clonar repositorio:

```bash
git clone https://github.com/JesusJC15/proyecto-arep.git
cd proyecto-arep
```

2. Levantar demo con Docker Compose (recomendado para demo local reproducible):

```bash
docker compose up --build -d
```

3. Rutas útiles:

- Frontend: http://localhost:4173
- Backend Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
- RAG status: http://localhost:8000/rag/status

4. Usuarios demo (preconfigurados):

- `ana.patient` / `demo123`
- `dr.suarez` / `demo123`

## Tests y validación

Backend (pytests):

```bash
cd backend
python -m pytest -q
```

Frontend (E2E):

```bash
cd frontend
npm install
npm run build
npm run test:e2e
```

## Documentación clave

- Runbook y operación: [docs/guides/runbook-final.md](docs/guides/runbook-final.md)
- Guion de demo: [docs/guides/demo-script.md](docs/guides/demo-script.md)
- Checklists: [docs/guides/final-checklists.md](docs/guides/final-checklists.md)
- Evaluación RAG: [docs/technical/rag-evaluation.md](docs/technical/rag-evaluation.md)

Reset completo de demo:

```bash
pwsh ./scripts/demo-reset.ps1
```

## Paquete académico y artefactos

- Paper y referencias: [paper/main.tex](paper/main.tex)
- Diagramas C4 y secuencias: [docs/architecture/README.md](docs/architecture/README.md)
- Slides (Reveal.js): [docs/presentation/index.html](docs/presentation/index.html)

## Infraestructura y despliegue

- Diagrama objetivo (Mermaid/MMD): [docs/architecture/06-aws-deployment.mmd](docs/architecture/06-aws-deployment.mmd)
- Blueprint y scripts para AWS: [infra/aws/README.md](infra/aws/README.md)

### Estado actual de despliegue

- Frontend: desplegado en S3 (URL arriba).
- Backend: preparado para despliegue; se puede instalar en EC2 / ECS / EKS o Lambda según preferencia — ver `infra/aws` para plantillas y notas.

## Limitaciones conocidas

- No existe validación clínica formal (investigación/propósito académico).
- Integración con sistemas FHIR es una proyección/documentada, no una integración productiva.
- El proyecto es una demo académica y de investigación; producción requeriría hardening adicional.
