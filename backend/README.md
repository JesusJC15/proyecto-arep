# Backend MVP

Backend base para la segunda entrega del proyecto AREP. Implementa los contratos minimos del MVP con `FastAPI`, repositorio en memoria y un flujo de triaje/RAG simplificado para alinear articulo, diagramas y codigo base.

## Endpoints

- `POST /auth/login`
- `POST /consultations`
- `GET /consultations/{id}`
- `POST /consultations/{id}/triage`
- `GET /consultations/{id}/recommendation`
- `GET /professional/cases`
- `GET /professional/cases/{id}`

## Ejecucion esperada

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload
```

## Usuarios demo

- `ana.patient` / `demo123`
- `dr.suarez` / `demo123`

## Nota

El backend usa un token tipo JWT de demostracion y un repositorio en memoria. Esto es suficiente para la segunda entrega, pero no representa una implementacion lista para produccion.
