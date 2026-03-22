from __future__ import annotations

from datetime import datetime, UTC

from app.schemas.domain import ConsultationRecord, Recommendation, SeverityLevel, TriageResult
from app.services.rag_service import rag_service


RED_FLAG_KEYWORDS = {
    "difficulty breathing",
    "shortness of breath",
    "chest pain",
    "fainting",
    "confusion",
    "severe pain",
    "rapid worsening",
}

INTENSITY_SCORE = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def _collect_terms(consultation: ConsultationRecord) -> list[str]:
    terms = [consultation.chief_complaint, consultation.context_notes]
    terms.extend(symptom.symptom for symptom in consultation.symptoms)
    terms.extend(condition for condition in consultation.chronic_conditions)
    return [term for term in terms if term]


def evaluate_consultation(consultation: ConsultationRecord) -> tuple[TriageResult, Recommendation]:
    joined_terms = " ".join(_collect_terms(consultation)).lower()
    highest_score = max(INTENSITY_SCORE.get(symptom.intensity, 1) for symptom in consultation.symptoms)
    has_red_flag = any(keyword in joined_terms for keyword in RED_FLAG_KEYWORDS)

    severity = SeverityLevel.LOW
    decision = "self_care"
    rationale = "No red flags identified in the submitted information."
    confidence = 0.74

    if highest_score >= INTENSITY_SCORE["medium"]:
        severity = SeverityLevel.MEDIUM
        decision = "watch_and_wait"
        rationale = "Moderate symptom intensity requires follow-up guidance and warning signs."
        confidence = 0.68

    if highest_score >= INTENSITY_SCORE["high"] or has_red_flag:
        severity = SeverityLevel.HIGH
        decision = "professional_review"
        rationale = "High symptom intensity or red-flag indicators require professional review."
        confidence = 0.61

    evidence_sources = rag_service.retrieve(_collect_terms(consultation))
    recommendation_text = {
        SeverityLevel.LOW: (
            "The case can remain in self-care mode with explicit warning signs and follow-up advice."
        ),
        SeverityLevel.MEDIUM: (
            "The case requires close monitoring, reinforced warning signs and an early professional check if symptoms persist."
        ),
        SeverityLevel.HIGH: (
            "The case should be escalated to a professional because the collected signals indicate higher risk or uncertainty."
        ),
    }[severity]

    triage_result = TriageResult(
        severity=severity,
        decision=decision,
        rationale=rationale,
        confidence=confidence,
        prompt_version="v0.1-academic-rag",
    )
    recommendation = Recommendation(
        summary=recommendation_text,
        disclaimer="Academic prototype only. This system does not replace professional clinical judgment.",
        evidence_sources=evidence_sources,
        generated_at=datetime.now(UTC),
    )
    return triage_result, recommendation
