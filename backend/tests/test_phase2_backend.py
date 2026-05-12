from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.security import create_access_token, hash_password
from app.core.settings import Settings
from app.main import create_app
from app.repositories.sql_repository import SQLRepository, UserModel
from app.schemas.domain import UserRole


@pytest.fixture(params=["sqlite", "postgres"], ids=["sqlite", "postgres"])
def client(request: pytest.FixtureRequest, tmp_path: Path) -> TestClient:
    postgres_url = os.getenv("TEST_POSTGRES_URL")
    if request.param == "postgres" and not postgres_url:
        pytest.skip("TEST_POSTGRES_URL is not configured")
    admin_engine = None
    schema_name = None
    if request.param == "postgres":
        schema_name = f"arep_test_{uuid4().hex}"
        admin_engine = create_engine(postgres_url, future=True, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema_name}"'))
        database_url = _postgres_url_with_schema(postgres_url, schema_name)
    else:
        database_url = f"sqlite:///{(tmp_path / 'arep_test.sqlite3').as_posix()}"
    settings = Settings(
        environment="test",
        database_url=database_url,
        jwt_secret="test-secret-key-with-32-bytes-minimum",
        access_token_ttl_minutes=30,
        seed_demo_data=True,
        cors_origins=("http://localhost:5173",),
        auth_rate_limit_count=5,
        auth_rate_limit_window_seconds=60,
        mutation_rate_limit_count=20,
        mutation_rate_limit_window_seconds=60,
    )
    try:
        with TestClient(create_app(settings)) as test_client:
            yield test_client
    finally:
        if admin_engine is not None and schema_name is not None:
            with admin_engine.connect() as connection:
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))
            admin_engine.dispose()


def _postgres_url_with_schema(base_url: str, schema_name: str) -> str:
    url = make_url(base_url)
    query = dict(url.query)
    query["options"] = f"-csearch_path={schema_name}"
    return url.update_query_dict(query).render_as_string(hide_password=False)


def login(client: TestClient, username: str, password: str, role: str) -> str:
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password, "role": role},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def create_payload(severity: str = "medium") -> dict:
    return {
        "chief_complaint": "Dolor toracico" if severity == "high" else "Tos persistente",
        "context_notes": "Empeora con actividad ligera" if severity == "high" else "Molestia moderada",
        "age_range": "adult",
        "chronic_conditions": ["hypertension"] if severity == "high" else [],
        "symptoms": [
            {
                "symptom": "Shortness of breath" if severity == "high" else "Tos",
                "duration": "24h",
                "intensity": severity,
                "notes": "En aumento",
            }
        ],
    }


def create_second_professional(client: TestClient) -> str:
    store: SQLRepository = client.app.state.store
    with store.SessionLocal() as session:
        if session.get(UserModel, "user-professional-2") is None:
            session.add(
                UserModel(
                    id="user-professional-2",
                    username="dr.lopez",
                    full_name="Dr. Lopez",
                    password_hash=hash_password("demo123"),
                    role=UserRole.PROFESSIONAL.value,
                )
            )
            session.commit()
    return login(client, "dr.lopez", "demo123", "professional")


def test_login_session_and_invalid_password(client: TestClient) -> None:
    token = login(client, "ana.patient", "demo123", "patient")

    session_response = client.get(
        "/auth/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert session_response.status_code == 200
    assert session_response.json()["role"] == "patient"

    invalid_response = client.post(
        "/auth/login",
        json={"username": "ana.patient", "password": "bad-pass", "role": "patient"},
    )
    assert invalid_response.status_code == 401


def test_invalid_and_expired_token_are_rejected(client: TestClient) -> None:
    tampered_response = client.get(
        "/auth/session",
        headers={"Authorization": "Bearer invalid.token"},
    )
    assert tampered_response.status_code == 401

    expired_token = create_access_token(
        user_id="user-patient-1",
        username="ana.patient",
        role=UserRole.PATIENT,
        secret="test-secret-key-with-32-bytes-minimum",
        algorithm="HS256",
        ttl_minutes=-1,
    )
    expired_response = client.get(
        "/auth/session",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired_response.status_code == 401


def test_missing_bearer_token_is_rejected(client: TestClient) -> None:
    missing_token_response = client.get("/auth/session")
    assert missing_token_response.status_code == 401


def test_role_restrictions_and_missing_recommendation(client: TestClient) -> None:
    patient_token = login(client, "ana.patient", "demo123", "patient")

    create_response = client.post(
        "/consultations",
        json=create_payload("medium"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert create_response.status_code == 200
    consultation_id = create_response.json()["id"]

    recommendation_response = client.get(
        f"/consultations/{consultation_id}/recommendation",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert recommendation_response.status_code == 409

    professional_cases_response = client.get(
        "/professional/cases",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert professional_cases_response.status_code == 403

    not_found_response = client.get(
        "/consultations/does-not-exist",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert not_found_response.status_code == 404


def test_patient_consultation_and_triage_flow(client: TestClient) -> None:
    patient_token = login(client, "ana.patient", "demo123", "patient")

    create_response = client.post(
        "/consultations",
        json=create_payload("medium"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert create_response.status_code == 200, create_response.text
    consultation_id = create_response.json()["id"]
    assert create_response.json()["status"] == "submitted"

    fetch_response = client.get(
        f"/consultations/{consultation_id}",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert fetch_response.status_code == 200

    triage_response = client.post(
        f"/consultations/{consultation_id}/triage",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert triage_response.status_code == 200, triage_response.text
    payload = triage_response.json()
    assert payload["status"] == "recommended"
    assert payload["triage_result"]["severity"] == "medium"
    assert payload["recommendation"]["evidence_sources"]
    assert payload["recommendation"]["retrieval_version"] == "rag-v1-hybrid-semantic"
    assert payload["recommendation"]["evidence_sources"][0]["retrieval_score"] > 0
    assert payload["recommendation"]["evidence_sources"][0]["document_id"]

    recommendation_response = client.get(
        f"/consultations/{consultation_id}/recommendation",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert recommendation_response.status_code == 200
    assert recommendation_response.json()["embedding_provider"] == "local"


def test_high_risk_consultation_creates_escalation_case_and_audit(client: TestClient) -> None:
    patient_token = login(client, "ana.patient", "demo123", "patient")
    professional_token = login(client, "dr.suarez", "demo123", "professional")

    create_response = client.post(
        "/consultations",
        json=create_payload("high"),
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    consultation_id = create_response.json()["id"]

    triage_response = client.post(
        f"/consultations/{consultation_id}/triage",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert triage_response.status_code == 200
    assert triage_response.json()["status"] == "escalated"

    cases_response = client.get(
        "/professional/cases",
        headers={"Authorization": f"Bearer {professional_token}"},
    )
    assert cases_response.status_code == 200
    cases = cases_response.json()
    assert any(item["consultation_id"] == consultation_id for item in cases)

    audit_events = client.app.state.store.list_audit_events()
    actions = [item.action for item in audit_events]
    assert "consultation.triage" in actions
    assert "consultation.escalated" in actions
    assert "auth.login" in actions
    assert "rag.retrieve" in actions


def test_professional_case_detail_assign_review_and_conflict(client: TestClient) -> None:
    professional_token = login(client, "dr.suarez", "demo123", "professional")
    second_professional_token = create_second_professional(client)

    cases_response = client.get(
        "/professional/cases",
        headers={"Authorization": f"Bearer {professional_token}"},
    )
    assert cases_response.status_code == 200
    case_id = cases_response.json()[0]["id"]

    detail_response = client.get(
        f"/professional/cases/{case_id}",
        headers={"Authorization": f"Bearer {professional_token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["consultation"]["symptoms"]

    assign_response = client.post(
        f"/professional/cases/{case_id}/assign",
        headers={"Authorization": f"Bearer {professional_token}"},
    )
    assert assign_response.status_code == 200, assign_response.text
    assert assign_response.json()["review_status"] == "assigned"
    assert assign_response.json()["assigned_professional_id"] == "user-professional-1"

    conflict_response = client.post(
        f"/professional/cases/{case_id}/assign",
        headers={"Authorization": f"Bearer {second_professional_token}"},
    )
    assert conflict_response.status_code == 409

    review_response = client.post(
        f"/professional/cases/{case_id}/review",
        headers={"Authorization": f"Bearer {professional_token}"},
    )
    assert review_response.status_code == 200, review_response.text
    payload = review_response.json()
    assert payload["review_status"] == "reviewed"
    assert payload["consultation"]["status"] == "reviewed"

    review_not_found = client.post(
        "/professional/cases/does-not-exist/review",
        headers={"Authorization": f"Bearer {professional_token}"},
    )
    assert review_not_found.status_code == 404


def test_rate_limit_metrics_and_readiness(client: TestClient, tmp_path: Path) -> None:
    limited_settings = Settings(
        environment="test",
        database_url=f"sqlite:///{(tmp_path / 'rate_limit.sqlite3').as_posix()}",
        jwt_secret="test-secret-key-with-32-bytes-minimum",
        seed_demo_data=True,
        cors_origins=("http://localhost:5173",),
        auth_rate_limit_count=1,
        auth_rate_limit_window_seconds=3600,
    )
    with TestClient(create_app(limited_settings)) as limited_client:
        first_login = limited_client.post(
            "/auth/login",
            json={"username": "ana.patient", "password": "demo123", "role": "patient"},
        )
        assert first_login.status_code == 200

        second_login = limited_client.post(
            "/auth/login",
            json={"username": "ana.patient", "password": "demo123", "role": "patient"},
        )
        assert second_login.status_code == 429

        readiness_response = limited_client.get("/ready")
        assert readiness_response.status_code == 200

        health_response = limited_client.get("/health")
        assert health_response.status_code == 200

        metrics_response = limited_client.get("/metrics")
        assert metrics_response.status_code == 200
        assert "arep_http_requests_total" in metrics_response.text

        rag_status_response = limited_client.get("/rag/status")
        assert rag_status_response.status_code == 200
        assert rag_status_response.json()["documents"] >= 6

        request_id = first_login.headers.get("X-Request-ID")
        assert request_id


def test_rag_dataset_metrics(client: TestClient) -> None:
    dataset_path = Path(__file__).resolve().parents[2] / "knowledge-base" / "evaluation" / "rag-evaluation-dataset.json"
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    rag_service = client.app.state.rag_service

    top1_hits = 0
    topk_hits = 0
    for case in payload["cases"]:
        trace = rag_service.retrieve(case["query_terms"])
        ranked_document_ids = [item.document_id for item in trace.evidence_sources]
        if ranked_document_ids and ranked_document_ids[0] in case["expected_document_ids"]:
            top1_hits += 1
        if any(item in case["expected_document_ids"] for item in ranked_document_ids):
            topk_hits += 1

    assert top1_hits >= 2
    assert topk_hits == len(payload["cases"])
