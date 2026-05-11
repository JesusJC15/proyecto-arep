# API Reference - AREP Endpoints

Complete documentation of all AREP API endpoints with examples, request/response formats, and error codes.

---

## Overview

**Base URL**: `http://localhost:8000` (local development)  
**Content-Type**: `application/json`  
**Authentication**: JWT Bearer token (in Authorization header)

## Meta Endpoints (No Auth Required)

### GET /health

Health check endpoint.

**Request**:
```bash
curl http://localhost:8000/health
```

**Response** (200):
```json
{"status": "ok"}
```

### GET /ready

Readiness check (includes database and service dependencies).

**Request**:
```bash
curl http://localhost:8000/ready
```

**Response** (200):
```json
{"status": "ready"}
```

**Response** (503 if not ready):
```json
{"status": "not-ready", "details": "Database connection failed"}
```

### GET /metrics

Prometheus-style metrics (if enabled).

**Request**:
```bash
curl http://localhost:8000/metrics
```

**Response** (200):
```
# HELP arep_api_requests_total Total API requests
# TYPE arep_api_requests_total counter
arep_api_requests_total{method="GET",endpoint="/health"} 42
...
```

### GET /rag/status

RAG pipeline status.

**Request**:
```bash
curl http://localhost:8000/rag/status
```

**Response** (200):
```json
{
  "corpus_version": "2026-05-phase4-expanded",
  "documents_in_corpus": 16,
  "chunks_in_index": 240,
  "embedding_provider": "local",
  "embedding_model": "tfidf-hash",
  "status": "ready"
}
```

---

## Authentication Endpoints

### POST /auth/login

Authenticate user and receive JWT token.

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ana.patient",
    "password": "demo123"
  }'
```

**Request Body**:
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-123",
    "username": "ana.patient",
    "role": "patient"
  }
}
```

**Response** (401 Unauthorized):
```json
{"detail": "Invalid credentials"}
```

**Response** (429 Too Many Requests - rate limited):
```json
{"detail": "Rate limit exceeded. Try again in 60 seconds."}
```

### GET /auth/session

Get current user session (requires auth).

**Request**:
```bash
curl http://localhost:8000/auth/session \
  -H "Authorization: Bearer <your-token>"
```

**Response** (200):
```json
{
  "user_id": "user-123",
  "username": "ana.patient",
  "role": "patient",
  "token_expires_at": "2026-05-10T14:30:00Z"
}
```

**Response** (401 Unauthorized):
```json
{"detail": "Not authenticated"}
```

---

## Consultation Endpoints (Requires Auth)

### POST /consultations

Create a new consultation.

**Request**:
```bash
curl -X POST http://localhost:8000/consultations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "patient_name": "John Doe",
    "chief_complaint": "Chest tightness",
    "symptoms": ["Chest discomfort", "Shortness of breath", "Fatigue"],
    "context_notes": "Symptoms started 2 hours ago after light activity"
  }'
```

**Request Body**:
```json
{
  "patient_name": "string (required)",
  "chief_complaint": "string (required)",
  "symptoms": ["string", "string"] (required, min 1),
  "context_notes": "string (optional)"
}
```

**Response** (201 Created):
```json
{
  "id": "consultation-abc123",
  "patient_user_id": "user-123",
  "patient_name": "John Doe",
  "chief_complaint": "Chest tightness",
  "symptoms": ["Chest discomfort", "Shortness of breath", "Fatigue"],
  "context_notes": "Symptoms started 2 hours ago after light activity",
  "created_at": "2026-05-10T12:30:00Z",
  "status": "intake"
}
```

**Response** (400 Bad Request):
```json
{"detail": "At least one symptom is required"}
```

### GET /consultations/{id}

Get consultation details.

**Request**:
```bash
curl http://localhost:8000/consultations/consultation-abc123 \
  -H "Authorization: Bearer <token>"
```

**Response** (200):
```json
{
  "id": "consultation-abc123",
  "patient_name": "John Doe",
  "chief_complaint": "Chest tightness",
  "symptoms": ["Chest discomfort", "Shortness of breath", "Fatigue"],
  "status": "triaged",
  "created_at": "2026-05-10T12:30:00Z",
  "triage_result": {
    "severity": "high",
    "decision": "professional_review",
    "reasoning": "Multiple cardiorespiratory symptoms..."
  }
}
```

**Response** (404 Not Found):
```json
{"detail": "Consultation not found"}
```

### POST /consultations/{id}/triage

Run triage and generate recommendation.

**Request**:
```bash
curl -X POST http://localhost:8000/consultations/consultation-abc123/triage \
  -H "Authorization: Bearer <token>"
```

**Response** (200):
```json
{
  "id": "consultation-abc123",
  "status": "triaged",
  "triage_result": {
    "severity": "high",
    "decision": "professional_review",
    "reasoning": "Patient presents with chest discomfort, dyspnea, and fatigue..."
  },
  "recommendation": {
    "decision": "professional_review",
    "summary": "Evidence suggests need for professional cardiorespiratory assessment",
    "evidence_sources": [
      {
        "id": "cardiac-symptoms-chunk-1",
        "title": "Cardiac Symptoms and Chest Pain",
        "snippet": "Chest pain with dyspnea warrants professional assessment...",
        "retrieval_score": 0.92,
        "rank": 1
      }
    ]
  }
}
```

**Response** (404):
```json
{"detail": "Consultation not found"}
```

**Response** (409 Conflict):
```json
{"detail": "Consultation already triaged"}
```

### GET /consultations/{id}/recommendation

Get recommendation for consultation.

**Request**:
```bash
curl http://localhost:8000/consultations/consultation-abc123/recommendation \
  -H "Authorization: Bearer <token>"
```

**Response** (200):
```json
{
  "decision": "professional_review",
  "summary": "Evidence suggests need for professional cardiorespiratory assessment",
  "evidence_sources": [
    {
      "id": "cardiac-symptoms",
      "title": "Cardiac Symptoms and Chest Pain",
      "snippet": "ACS encompasses unstable angina, STEMI, and NSTEMI...",
      "retrieval_score": 0.88
    }
  ]
}
```

**Response** (404):
```json
{"detail": "Recommendation not found for this consultation"}
```

---

## Professional Cases Endpoints (Requires Professional Role)

### GET /professional/cases

List all escalated cases (professional only).

**Request**:
```bash
curl http://localhost:8000/professional/cases \
  -H "Authorization: Bearer <professional-token>"
```

**Response** (200):
```json
{
  "cases": [
    {
      "id": "case-123",
      "consultation_id": "consultation-abc123",
      "patient_alias": "Patient J.D.",
      "severity": "high",
      "chief_complaint": "Chest tightness",
      "status": "open",
      "created_at": "2026-05-10T12:30:00Z",
      "recommendation_summary": "Professional review recommended"
    }
  ],
  "total": 3,
  "open": 3,
  "closed": 0
}
```

**Response** (403 Forbidden):
```json
{"detail": "Only professionals can access this endpoint"}
```

### GET /professional/cases/{id}

Get detailed case information.

**Request**:
```bash
curl http://localhost:8000/professional/cases/case-123 \
  -H "Authorization: Bearer <professional-token>"
```

**Response** (200):
```json
{
  "id": "case-123",
  "consultation_id": "consultation-abc123",
  "patient_alias": "Patient J.D.",
  "severity": "high",
  "chief_complaint": "Chest tightness",
  "symptoms": ["Chest discomfort", "Shortness of breath"],
  "context": "Symptoms started 2 hours ago",
  "recommendation": {
    "decision": "professional_review",
    "summary": "...",
    "evidence_sources": [...]
  },
  "status": "open",
  "assigned_to": "dr.suarez",
  "created_at": "2026-05-10T12:30:00Z",
  "notes": []
}
```

### POST /professional/cases/{id}/assign

Assign case to professional.

**Request**:
```bash
curl -X POST http://localhost:8000/professional/cases/case-123/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <professional-token>" \
  -d '{"assigned_to": "dr.suarez"}'
```

**Response** (200):
```json
{"status": "assigned", "assigned_to": "dr.suarez"}
```

### POST /professional/cases/{id}/review

Submit case review and close.

**Request**:
```bash
curl -X POST http://localhost:8000/professional/cases/case-123/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <professional-token>" \
  -d '{
    "professional_notes": "Patient shows signs of cardiac stress. Recommend EKG and troponin levels.",
    "action_taken": "referral_to_emergency",
    "follow_up_required": true,
    "follow_up_days": 3
  }'
```

**Request Body**:
```json
{
  "professional_notes": "string (required)",
  "action_taken": "self_care|watchful_waiting|specialist_referral|emergency" (required),
  "follow_up_required": "boolean (optional)",
  "follow_up_days": "integer (optional)"
}
```

**Response** (200):
```json
{
  "id": "case-123",
  "status": "closed",
  "reviewed_by": "dr.suarez",
  "reviewed_at": "2026-05-10T14:00:00Z",
  "professional_notes": "Patient shows signs of cardiac stress..."
}
```

---

## RAG Source Endpoint

### GET /rag/source

Retrieve clinical guideline source document.

**Request**:
```bash
curl "http://localhost:8000/rag/source?uri=knowledge-base/clinical-guidelines/cardiac-symptoms.md" \
  -H "Authorization: Bearer <token>"
```

**Query Parameters**:
- `uri` (required): Path to document (e.g., `knowledge-base/clinical-guidelines/cardiac-symptoms.md`)

**Response** (200):
```markdown
# Cardiac Symptoms and Chest Pain

Chest pain is a cardinal symptom of acute coronary syndrome (ACS)...
```

**Response** (400 Bad Request):
```json
{"detail": "Invalid URI: path traversal detected"}
```

**Response** (404 Not Found):
```json
{"detail": "Source document not found"}
```

---

## Error Responses

### Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Invalid input or missing required field |
| 401 | Unauthorized | Token missing or invalid |
| 403 | Forbidden | User lacks required role/permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Invalid state (e.g., already triaged) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Database/RAG service down |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

- **Authentication**: 10 requests per minute per IP
- **Mutations** (POST/PUT): 20 requests per minute per user
- **Queries** (GET): 100 requests per minute per user

When rate limited (429):
```json
{"detail": "Rate limit exceeded. Retry after 60 seconds."}
```

---

## Authentication Header

Include JWT token in all authenticated requests:

```bash
curl -H "Authorization: Bearer <your-token>" \
  http://localhost:8000/consultations
```

Token format: `Authorization: Bearer eyJhbGciOiJIUzI1NiIs...`

---

## Examples

### Complete Patient Flow

```bash
# 1. Login as patient
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ana.patient","password":"demo123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 2. Create consultation
CONSULT=$(curl -s -X POST http://localhost:8000/consultations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "patient_name":"Ana","chief_complaint":"Chest pain",
    "symptoms":["Chest discomfort","Shortness of breath"]
  }' | grep -o '"id":"[^"]*' | cut -d'"' -f4)

# 3. Run triage
curl -s -X POST http://localhost:8000/consultations/$CONSULT/triage \
  -H "Authorization: Bearer $TOKEN"

# 4. Get recommendation
curl -s http://localhost:8000/consultations/$CONSULT/recommendation \
  -H "Authorization: Bearer $TOKEN"
```

---

**Last Updated**: May 10, 2026  
**API Version**: 1.0
