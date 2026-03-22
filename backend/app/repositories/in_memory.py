from __future__ import annotations

from datetime import datetime, UTC
from uuid import uuid4

from app.schemas.domain import (
    ConsultationCreate,
    ConsultationRecord,
    ConsultationStatus,
    DemoUser,
    EvidenceSource,
    EscalationCase,
    Recommendation,
    SeverityLevel,
    SymptomEntry,
    TriageResult,
    UserRole,
)


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, DemoUser] = {}
        self.consultations: dict[str, ConsultationRecord] = {}
        self.escalations: dict[str, EscalationCase] = {}
        self._seed()

    def _seed(self) -> None:
        patient = DemoUser(
            id="user-patient-1",
            username="ana.patient",
            full_name="Ana Torres",
            password="demo123",
            role=UserRole.PATIENT,
        )
        professional = DemoUser(
            id="user-professional-1",
            username="dr.suarez",
            full_name="Dra. Suarez",
            password="demo123",
            role=UserRole.PROFESSIONAL,
        )
        self.users[patient.id] = patient
        self.users[professional.id] = professional
        self._seed_escalated_case(patient.id)

    def _seed_escalated_case(self, patient_user_id: str) -> None:
        consultation = ConsultationRecord(
            id="seed-consultation-1",
            patient_user_id=patient_user_id,
            chief_complaint="Chest discomfort with persistent shortness of breath",
            context_notes="Symptoms increased after light physical effort during the morning.",
            age_range="adult",
            chronic_conditions=["hypertension"],
            symptoms=[
                SymptomEntry(
                    id="seed-symptom-1",
                    symptom="Chest discomfort",
                    duration="24h",
                    intensity="high",
                    notes="Intermittent but worsening",
                ),
                SymptomEntry(
                    id="seed-symptom-2",
                    symptom="Shortness of breath",
                    duration="12h",
                    intensity="high",
                    notes="Triggered by low effort",
                ),
            ],
            status=ConsultationStatus.ESCALATED,
            created_at=datetime.now(UTC),
            triage_result=TriageResult(
                severity=SeverityLevel.HIGH,
                decision="professional_review",
                rationale="High intensity symptoms and red-flag pattern require escalation.",
                confidence=0.62,
                prompt_version="v0.1-academic-rag",
            ),
            recommendation=Recommendation(
                summary="Escalate to professional review and preserve the evidence trace for clinician assessment.",
                disclaimer="Academic prototype only. This system does not replace professional clinical judgment.",
                evidence_sources=[
                    EvidenceSource(
                        id="seed-source-1",
                        title="Red Flags for Escalation",
                        source_type="markdown",
                        uri="knowledge-base/clinical-guidelines/red-flags.md",
                        snippet="High intensity symptoms and rapid worsening trigger professional review.",
                    )
                ],
                generated_at=datetime.now(UTC),
            ),
        )
        escalation = EscalationCase(
            id="seed-case-1",
            consultation_id=consultation.id,
            assigned_professional_id=None,
            review_status="pending",
            reason="High severity or low confidence recommendation",
            created_at=consultation.created_at,
            triage_result=consultation.triage_result,
            recommendation=consultation.recommendation,
        )
        self.consultations[consultation.id] = consultation
        self.escalations[escalation.id] = escalation

    def get_user_by_credentials(self, username: str, password: str, role: UserRole) -> DemoUser | None:
        for user in self.users.values():
            if user.username == username and user.password == password and user.role == role:
                return user
        return None

    def get_user(self, user_id: str) -> DemoUser | None:
        return self.users.get(user_id)

    def create_consultation(self, payload: ConsultationCreate, patient_user_id: str) -> ConsultationRecord:
        consultation_id = str(uuid4())
        symptoms = [
            SymptomEntry(
                id=str(uuid4()),
                symptom=item.symptom,
                duration=item.duration,
                intensity=item.intensity,
                notes=item.notes,
            )
            for item in payload.symptoms
        ]
        record = ConsultationRecord(
            id=consultation_id,
            patient_user_id=patient_user_id,
            chief_complaint=payload.chief_complaint,
            context_notes=payload.context_notes,
            age_range=payload.age_range,
            chronic_conditions=payload.chronic_conditions,
            symptoms=symptoms,
            status=ConsultationStatus.SUBMITTED,
            created_at=datetime.now(UTC),
        )
        self.consultations[consultation_id] = record
        return record

    def get_consultation(self, consultation_id: str) -> ConsultationRecord | None:
        return self.consultations.get(consultation_id)

    def save_triage(
        self,
        consultation_id: str,
        triage_result: TriageResult,
        recommendation: Recommendation,
    ) -> ConsultationRecord:
        consultation = self.consultations[consultation_id]
        consultation.triage_result = triage_result
        consultation.recommendation = recommendation
        consultation.status = ConsultationStatus.RECOMMENDED
        if triage_result.severity == SeverityLevel.HIGH or triage_result.decision == "professional_review":
            consultation.status = ConsultationStatus.ESCALATED
            self._create_escalation_case(consultation, triage_result, recommendation)
        self.consultations[consultation_id] = consultation
        return consultation

    def _create_escalation_case(
        self,
        consultation: ConsultationRecord,
        triage_result: TriageResult,
        recommendation: Recommendation,
    ) -> None:
        existing = next(
            (case for case in self.escalations.values() if case.consultation_id == consultation.id),
            None,
        )
        if existing:
            return
        escalation = EscalationCase(
            id=str(uuid4()),
            consultation_id=consultation.id,
            assigned_professional_id=None,
            reason="High severity or low confidence recommendation",
            created_at=datetime.now(UTC),
            triage_result=triage_result,
            recommendation=recommendation,
        )
        self.escalations[escalation.id] = escalation

    def list_escalations(self) -> list[EscalationCase]:
        return sorted(self.escalations.values(), key=lambda item: item.created_at, reverse=True)

    def get_escalation(self, case_id: str) -> EscalationCase | None:
        return self.escalations.get(case_id)


store = InMemoryStore()
