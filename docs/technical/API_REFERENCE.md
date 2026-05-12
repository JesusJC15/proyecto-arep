# API Reference - AREP Endpoints

Referencia funcional de la API FastAPI de AREP. La base local por defecto es `http://localhost:8000`.

## Convenciones

- Autenticacion: usar `Authorization: Bearer <token>` en todas las rutas protegidas.
- Roles: `patient` y `professional`.
- Formato de error: `{"detail": "..."}`.
- Identificadores: strings opacos generados por el repositorio.

## Endpoints de meta

### GET /

Estado general de la aplicacion.

Respuesta ejemplo:

```json
{
	"project": "AREP Triage MVP",
	"status": "ready",
	"docs": "/docs",
	"database_backend": "postgresql"
}
```

### GET /health

Verificacion simple de salud.

Respuesta:

```json
{"status": "ok"}
```

### GET /ready

Verifica que la persistencia y el servicio RAG esten listos.

Respuesta:

```json
{"status": "ready"}
```

### GET /metrics

Expone metrics en texto plano para Prometheus.

### GET /rag/status

Devuelve el estado del corpus e indice RAG.

Respuesta ejemplo:

```json
{
	"corpus_version": "2026-05-phase3",
	"retrieval_version": "hybrid-local-v1",
	"embedding_provider": "local",
	"embedding_model": "hashed-tfidf-v1",
	"documents": 14,
	"chunks": 42,
	"index_version": "rag-index-v1",
	"index_artifact_path": "artifacts/rag-index.json"
}
```

### GET /rag/source?uri=...

Devuelve el contenido original de una fuente del corpus en Markdown.

## Autenticacion

### POST /auth/login

Inicia sesion con usuario, contrasena y rol.

Request ejemplo:

```json
{
	"username": "ana.patient",
	"password": "demo123",
	"role": "patient"
}
```

Response ejemplo:

```json
{
	"access_token": "eyJhbGciOi...",
	"token_type": "bearer",
	"user": {
		"id": "user-patient-ana",
		"username": "ana.patient",
		"full_name": "Ana Patient",
		"role": "patient"
	}
}
```

Errores tipicos: `401` credenciales invalidas, `429` limite de tasa.

### GET /auth/session

Recupera el usuario autenticado del token actual.

Response ejemplo:

```json
{
	"id": "user-patient-ana",
	"username": "ana.patient",
	"full_name": "Ana Patient",
	"role": "patient"
}
```

## Consultas

### POST /consultations

Reserva una nueva consulta. Requiere rol `patient`.

Request ejemplo:

```json
{
	"chief_complaint": "Fiebre y tos",
	"context_notes": "Sintomas desde hace 2 dias",
	"age_range": "adult",
	"chronic_conditions": ["asma"],
	"symptoms": [
		{
			"symptom": "fiebre",
			"duration": "2 dias",
			"intensity": "medium",
			"notes": "picos nocturnos"
		}
	]
}
```

### GET /consultations/{id}

Consulta un registro por id. El paciente solo puede ver sus propios casos.

### POST /consultations/{id}/triage

Ejecuta el triage y genera recomendacion con evidencia RAG.

Respuesta clave:

```json
{
	"id": "consultation-123",
	"status": "recommended",
	"triage_result": {
		"severity": "medium",
		"decision": "professional_review",
		"rationale": "...",
		"confidence": 0.82,
		"prompt_version": "triage-v1"
	},
	"recommendation": {
		"summary": "...",
		"disclaimer": "...",
		"evidence_sources": [],
		"generated_at": "2026-05-11T12:00:00Z",
		"retrieval_version": "hybrid-local-v1",
		"embedding_provider": "local",
		"embedding_model": "hashed-tfidf-v1",
		"corpus_version": "2026-05-phase3"
	}
}
```

Errores tipicos: `403` si la consulta no pertenece al paciente, `409` si ya no se puede recalcular.

### GET /consultations/{id}/recommendation

Recupera la recomendacion generada tras el triage.

## Bandeja profesional

### GET /professional/cases

Lista los casos escalados. Requiere rol `professional`.

### GET /professional/cases/{id}

Devuelve el detalle de un caso profesional.

### POST /professional/cases/{id}/assign

Asigna el caso al profesional autenticado.

### POST /professional/cases/{id}/review

Marca el caso como revisado.

## Códigos de error comunes

- `400`: payload invalido.
- `401`: token ausente o invalido.
- `403`: rol o acceso insuficiente.
- `404`: recurso no encontrado.
- `409`: estado incompatible para la operacion.
- `429`: limite de tasa alcanzado.
- `500`: error interno.
