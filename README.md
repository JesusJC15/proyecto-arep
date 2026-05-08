# AREP - Entrega final integral

AREP es una plataforma academica de triaje medico asistido por IA con autenticacion por roles, flujo paciente-profesional, recomendacion trazable y un pipeline RAG reproducible. La entrega final deja una demo ejecutable con `Docker Compose`, una proyeccion AWS defendible y un paquete academico listo para sustentacion.

## Que incluye

- frontend React con evidencia visible por score, rank y procedencia
- backend FastAPI con JWT, auditoria, metricas y `rag/status`
- Postgres como base oficial de demo
- corpus versionado con evaluacion RAG reproducible
- runbook final, guion de demo y checklists de cierre
- blueprint AWS base para `red + app + datos`
- paper alineado y slides HTML en `Reveal.js`

## Arquitectura resumida

- `frontend`: canal paciente y canal profesional
- `backend`: API, triage por reglas, retrieval semantico local y trazabilidad
- `postgres`: persistencia oficial de demo
- `knowledge-base`: corpus curado y dataset de evaluacion
- `artifacts`: indice RAG reproducible en runtime

## Arranque oficial

```bash
docker compose up --build -d
```

URLs principales:

- App: [http://localhost:4173](http://localhost:4173)
- Health: [http://localhost:8000/health](http://localhost:8000/health)
- Ready: [http://localhost:8000/ready](http://localhost:8000/ready)
- Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- RAG status: [http://localhost:8000/rag/status](http://localhost:8000/rag/status)

Usuarios demo:

- `ana.patient / demo123`
- `dr.suarez / demo123`

## Validacion

Backend:

```bash
cd backend
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm install
npm run build
npm run test:e2e
```

## Demo y operacion

- Runbook final: [docs/runbook-final.md](docs/runbook-final.md)
- Guion de demo: [docs/demo-script.md](docs/demo-script.md)
- Checklists finales: [docs/final-checklists.md](docs/final-checklists.md)
- Evaluacion RAG: [docs/rag-evaluation.md](docs/rag-evaluation.md)

Reset completo de demo:

```bash
pwsh ./scripts/demo-reset.ps1
```

## Paquete academico

- Paper: [paper/main.tex](paper/main.tex)
- Diagramas: [docs/architecture/README.md](docs/architecture/README.md)
- Slides HTML: [docs/presentation/index.html](docs/presentation/index.html)

## Blueprint AWS

- Diagrama objetivo: [docs/architecture/06-aws-deployment.mmd](docs/architecture/06-aws-deployment.mmd)
- Blueprint base: [infra/aws/README.md](infra/aws/README.md)

## Limites

- No hay despliegue real en AWS en esta fase
- No hay validacion clinica formal
- El RAG sigue siendo academico aunque ya es trazable y evaluable
- FHIR se mantiene como proyeccion, no como integracion activa
