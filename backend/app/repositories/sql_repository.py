from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine, inspect, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.types import JSON

from app.core.security import hash_password, verify_password
from app.core.tracing import trace_span
from app.schemas.domain import (
    AuditEvent,
    CorpusChunkRecord,
    CorpusDocumentRecord,
    ConsultationCreate,
    ConsultationRecord,
    ConsultationStatus,
    EvidenceSource,
    ProfessionalCaseDetail,
    ProfessionalCaseSummary,
    RAGStatus,
    Recommendation,
    RetrievalTrace,
    SeverityLevel,
    SymptomEntry,
    TriageResult,
    UserRecord,
    UserRole,
)


class Base(DeclarativeBase):
    pass


class SchemaVersionModel(Base):
    __tablename__ = "schema_versions"

    version: Mapped[str] = mapped_column(String(32), primary_key=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)


class ConsultationModel(Base):
    __tablename__ = "consultations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    patient_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    chief_complaint: Mapped[str] = mapped_column(String(255), nullable=False)
    context_notes: Mapped[str] = mapped_column(Text, nullable=False)
    age_range: Mapped[str] = mapped_column(String(64), nullable=False)
    chronic_conditions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    symptoms: Mapped[list["SymptomModel"]] = relationship(cascade="all, delete-orphan")
    triage_result: Mapped["TriageResultModel | None"] = relationship(cascade="all, delete-orphan", uselist=False)
    recommendation: Mapped["RecommendationModel | None"] = relationship(cascade="all, delete-orphan", uselist=False)


class SymptomModel(Base):
    __tablename__ = "symptoms"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), nullable=False)
    symptom: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[str] = mapped_column(String(128), nullable=False)
    intensity: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class TriageResultModel(Base):
    __tablename__ = "triage_results"

    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), primary_key=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    decision: Mapped[str] = mapped_column(String(64), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(128), nullable=False)


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), primary_key=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retrieval_version: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    corpus_version: Mapped[str] = mapped_column(String(64), nullable=False)

    evidence_sources: Mapped[list["EvidenceSourceModel"]] = relationship(cascade="all, delete-orphan")


class EvidenceSourceModel(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    recommendation_consultation_id: Mapped[str] = mapped_column(ForeignKey("recommendations.consultation_id"), nullable=False)
    document_id: Mapped[str] = mapped_column(String(128), nullable=False)
    chunk_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    uri: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieval_method: Mapped[str] = mapped_column(String(64), nullable=False)
    match_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    matched_terms: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class EscalationCaseModel(Base):
    __tablename__ = "escalation_cases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), unique=True, nullable=False)
    assigned_professional_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    outcome: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[dict[str, object] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CorpusDocumentModel(Base):
    __tablename__ = "corpus_documents"

    document_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_uri: Mapped[str] = mapped_column(Text, nullable=False)
    clinical_topic: Mapped[str] = mapped_column(String(128), nullable=False)
    audience: Mapped[str] = mapped_column(String(64), nullable=False)
    publication_or_revision_date: Mapped[str] = mapped_column(String(32), nullable=False)
    curation_status: Mapped[str] = mapped_column(String(64), nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    license_or_usage_note: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False)
    corpus_version: Mapped[str] = mapped_column(String(64), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CorpusChunkModel(Base):
    __tablename__ = "corpus_chunks"

    chunk_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("corpus_documents.document_id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False)


class RagIndexRunModel(Base):
    __tablename__ = "rag_index_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    corpus_version: Mapped[str] = mapped_column(String(64), nullable=False)
    retrieval_version: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    documents: Mapped[int] = mapped_column(Integer, nullable=False)
    chunks: Mapped[int] = mapped_column(Integer, nullable=False)
    index_artifact_path: Mapped[str] = mapped_column(Text, nullable=False)
    built_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RagRetrievalTraceModel(Base):
    __tablename__ = "rag_retrieval_traces"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    consultation_id: Mapped[str | None] = mapped_column(ForeignKey("consultations.id"), nullable=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_terms: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    retrieval_version: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    corpus_version: Mapped[str] = mapped_column(String(64), nullable=False)
    index_version: Mapped[str] = mapped_column(String(64), nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    candidates_considered: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_sources_json: Mapped[list[dict[str, object]]] = mapped_column("evidence_sources", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SQLRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.sqlite_file: Path | None = None
        if database_url.startswith("sqlite:///"):
            db_file = Path(database_url.removeprefix("sqlite:///")).resolve()
            db_file.parent.mkdir(parents=True, exist_ok=True)
            self.sqlite_file = db_file
            self.engine = create_engine(database_url, future=True, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(database_url, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    def initialize(self, seed_demo_data: bool) -> None:
        with trace_span("repository.initialize", database_url=self.database_url):
            if self._needs_schema_reset():
                if self.sqlite_file is not None and self.sqlite_file.exists():
                    self.engine.dispose()
                    self.sqlite_file.unlink()
                    self.engine = create_engine(self.database_url, future=True, connect_args={"check_same_thread": False})
                    self.SessionLocal.configure(bind=self.engine)
                else:
                    Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
            with self.SessionLocal() as session:
                if session.get(SchemaVersionModel, "2026-05-phase3") is None:
                    session.add(SchemaVersionModel(version="2026-05-phase3", applied_at=datetime.now(UTC)))
                    session.commit()
        if seed_demo_data:
            self.seed_demo_data()

    def dispose(self) -> None:
        self.engine.dispose()

    def healthcheck(self) -> None:
        with self.SessionLocal() as session:
            session.execute(select(1)).scalar_one()

    def seed_demo_data(self) -> None:
        with self.SessionLocal() as session:
            existing = session.scalar(select(UserModel).limit(1))
            if existing is not None:
                return
            patient = UserModel(
                id="user-patient-1",
                username="ana.patient",
                full_name="Ana Torres",
                password_hash=hash_password("demo123"),
                role=UserRole.PATIENT.value,
            )
            professional = UserModel(
                id="user-professional-1",
                username="dr.suarez",
                full_name="Dra. Suarez",
                password_hash=hash_password("demo123"),
                role=UserRole.PROFESSIONAL.value,
            )
            session.add_all([patient, professional])
            session.commit()
            consultation = ConsultationModel(
                id="seed-consultation-1",
                patient_user_id=patient.id,
                chief_complaint="Chest discomfort with persistent shortness of breath",
                context_notes="Symptoms increased after light physical effort during the morning.",
                age_range="adult",
                chronic_conditions=["hypertension"],
                status=ConsultationStatus.ESCALATED.value,
                created_at=datetime.now(UTC),
            )
            consultation.symptoms = [
                SymptomModel(
                    id="seed-symptom-1",
                    symptom="Chest discomfort",
                    duration="24h",
                    intensity="high",
                    notes="Intermittent but worsening",
                ),
                SymptomModel(
                    id="seed-symptom-2",
                    symptom="Shortness of breath",
                    duration="12h",
                    intensity="high",
                    notes="Triggered by low effort",
                ),
            ]
            consultation.triage_result = TriageResultModel(
                consultation_id=consultation.id,
                severity=SeverityLevel.HIGH.value,
                decision="professional_review",
                rationale="High intensity symptoms and red-flag pattern require escalation.",
                confidence=0.62,
                prompt_version="v0.4-rag-phase3",
            )
            recommendation = RecommendationModel(
                consultation_id=consultation.id,
                summary="Escalar a revision profesional y conservar la evidencia trazable para analisis clinico.",
                disclaimer="Prototipo academico. Este sistema no reemplaza el juicio clinico profesional.",
                generated_at=datetime.now(UTC),
                retrieval_version="rag-v1-hybrid-semantic",
                embedding_provider="local",
                embedding_model="hashed-tfidf-v1",
                corpus_version="2026-05-phase3",
            )
            recommendation.evidence_sources = [
                EvidenceSourceModel(
                    id="seed-source-1",
                    document_id="red-flags",
                    chunk_id="red-flags-chunk-0",
                    title="Red Flags for Escalation",
                    source_type="academic_synthesis",
                    uri="knowledge-base/clinical-guidelines/red-flags.md",
                    snippet="Red flags include chest pain, chest pressure, shortness of breath, fainting, confusion, severe weakness, cyanosis, and rapid worsening over a short period.",
                    retrieval_score=0.9123,
                    rank=1,
                    retrieval_method="local_hybrid",
                    match_rationale="Caso semilla alineado con senales de alarma cardiorrespiratoria.",
                    matched_terms=["chest", "pain", "breathing", "worsening"],
                ),
                EvidenceSourceModel(
                    id="seed-source-2",
                    document_id="chest-pain-escalation",
                    chunk_id="chest-pain-escalation-chunk-0",
                    title="Chest Pain Escalation Signals",
                    source_type="academic_synthesis",
                    uri="knowledge-base/clinical-guidelines/chest-pain-escalation.md",
                    snippet="Chest pain, chest discomfort, or pressure associated with fatigue, dizziness, or shortness of breath should be handled as a higher risk pattern in a triage setting.",
                    retrieval_score=0.8742,
                    rank=2,
                    retrieval_method="local_hybrid",
                    match_rationale="Caso semilla relacionado con dolor toracico y disnea.",
                    matched_terms=["chest", "pain", "shortness", "breathing"],
                ),
            ]
            consultation.recommendation = recommendation
            session.add(consultation)
            session.flush()
            session.add(
                EscalationCaseModel(
                    id="seed-case-1",
                    consultation_id=consultation.id,
                    assigned_professional_id=None,
                    review_status="pending",
                    reason="High severity or low confidence recommendation",
                    created_at=consultation.created_at,
                    reviewed_at=None,
                )
            )
            session.commit()

    def _needs_schema_reset(self) -> bool:
        inspector = inspect(self.engine)
        table_names = set(inspector.get_table_names())
        if not table_names:
            return False
        required_tables = {
            "users",
            "consultations",
            "symptoms",
            "triage_results",
            "recommendations",
            "evidence_sources",
            "escalation_cases",
            "audit_events",
            "corpus_documents",
            "corpus_chunks",
            "rag_index_runs",
            "rag_retrieval_traces",
        }
        if not required_tables.issubset(table_names):
            return True
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        recommendation_columns = {column["name"] for column in inspector.get_columns("recommendations")}
        evidence_columns = {column["name"] for column in inspector.get_columns("evidence_sources")}
        evidence_id_length = next(
            (column["type"].length for column in inspector.get_columns("evidence_sources") if column["name"] == "id"),
            None,
        )
        return (
            "password_hash" not in user_columns
            or "retrieval_version" not in recommendation_columns
            or "document_id" not in evidence_columns
            or (evidence_id_length is not None and evidence_id_length < 128)
        )

    def get_user(self, user_id: str) -> UserRecord | None:
        with self.SessionLocal() as session:
            model = session.get(UserModel, user_id)
            return self._build_user(model) if model else None

    def get_user_by_credentials(self, username: str, password: str, role: UserRole) -> UserRecord | None:
        with trace_span("repository.authenticate", username=username, role=role.value):
            with self.SessionLocal() as session:
                model = session.scalar(select(UserModel).where(UserModel.username == username, UserModel.role == role.value))
                if model is None or not verify_password(password, model.password_hash):
                    return None
                return self._build_user(model)

    def create_consultation(self, payload: ConsultationCreate, patient_user_id: str) -> ConsultationRecord:
        with trace_span("repository.create_consultation", patient_user_id=patient_user_id):
            with self.SessionLocal() as session:
                consultation = ConsultationModel(
                    id=str(uuid4()),
                    patient_user_id=patient_user_id,
                    chief_complaint=payload.chief_complaint,
                    context_notes=payload.context_notes,
                    age_range=payload.age_range,
                    chronic_conditions=payload.chronic_conditions,
                    status=ConsultationStatus.SUBMITTED.value,
                    created_at=datetime.now(UTC),
                )
                consultation.symptoms = [
                    SymptomModel(
                        id=str(uuid4()),
                        symptom=item.symptom,
                        duration=item.duration,
                        intensity=item.intensity,
                        notes=item.notes,
                    )
                    for item in payload.symptoms
                ]
                session.add(consultation)
                session.commit()
                session.refresh(consultation)
                return self._build_consultation(consultation)

    def get_consultation(self, consultation_id: str) -> ConsultationRecord | None:
        with self.SessionLocal() as session:
            model = session.get(ConsultationModel, consultation_id)
            return self._build_consultation(model) if model else None

    def save_triage(self, consultation_id: str, triage_result: TriageResult, recommendation: Recommendation) -> ConsultationRecord:
        with trace_span("repository.save_triage", consultation_id=consultation_id):
            with self.SessionLocal() as session:
                consultation = session.get(ConsultationModel, consultation_id)
                if consultation is None:
                    raise KeyError(consultation_id)
                consultation.status = (
                    ConsultationStatus.ESCALATED.value
                    if triage_result.decision == "professional_review"
                    else ConsultationStatus.RECOMMENDED.value
                )
                consultation.triage_result = TriageResultModel(
                    consultation_id=consultation.id,
                    severity=triage_result.severity.value,
                    decision=triage_result.decision,
                    rationale=triage_result.rationale,
                    confidence=triage_result.confidence,
                    prompt_version=triage_result.prompt_version,
                )
                recommendation_model = RecommendationModel(
                    consultation_id=consultation.id,
                    summary=recommendation.summary,
                    disclaimer=recommendation.disclaimer,
                    generated_at=recommendation.generated_at,
                    retrieval_version=recommendation.retrieval_version,
                    embedding_provider=recommendation.embedding_provider,
                    embedding_model=recommendation.embedding_model,
                    corpus_version=recommendation.corpus_version,
                )
                recommendation_model.evidence_sources = [
                    EvidenceSourceModel(
                        id=source.id,
                        document_id=source.document_id,
                        chunk_id=source.chunk_id,
                        title=source.title,
                        source_type=source.source_type,
                        uri=source.uri,
                        snippet=source.snippet,
                        retrieval_score=source.retrieval_score,
                        rank=source.rank,
                        retrieval_method=source.retrieval_method,
                        match_rationale=source.match_rationale,
                        matched_terms=source.matched_terms,
                    )
                    for source in recommendation.evidence_sources
                ]
                consultation.recommendation = recommendation_model
                if consultation.status == ConsultationStatus.ESCALATED.value:
                    existing_case = session.scalar(select(EscalationCaseModel).where(EscalationCaseModel.consultation_id == consultation.id))
                    if existing_case is None:
                        session.add(
                            EscalationCaseModel(
                                id=str(uuid4()),
                                consultation_id=consultation.id,
                                assigned_professional_id=None,
                                review_status="pending",
                                reason="High severity or low confidence recommendation",
                                created_at=datetime.now(UTC),
                                reviewed_at=None,
                            )
                        )
                session.commit()
                session.refresh(consultation)
                return self._build_consultation(consultation)

    def list_escalations(self) -> list[ProfessionalCaseSummary]:
        with self.SessionLocal() as session:
            rows = session.scalars(select(EscalationCaseModel).order_by(EscalationCaseModel.created_at.desc())).all()
            result: list[ProfessionalCaseSummary] = []
            for row in rows:
                consultation = session.get(ConsultationModel, row.consultation_id)
                if consultation is None or consultation.triage_result is None:
                    continue
                result.append(
                    ProfessionalCaseSummary(
                        id=row.id,
                        consultation_id=row.consultation_id,
                        severity=SeverityLevel(consultation.triage_result.severity),
                        review_status=row.review_status,
                        reason=row.reason,
                        created_at=row.created_at,
                    )
                )
            return result

    def get_professional_case(self, case_id: str) -> ProfessionalCaseDetail | None:
        with self.SessionLocal() as session:
            row = session.get(EscalationCaseModel, case_id)
            if row is None:
                return None
            consultation = session.get(ConsultationModel, row.consultation_id)
            if consultation is None:
                return None
            return self._build_professional_case(row, consultation)

    def assign_case(self, case_id: str, professional_id: str) -> ProfessionalCaseDetail | None:
        with trace_span("repository.assign_case", case_id=case_id, professional_id=professional_id):
            with self.SessionLocal() as session:
                row = session.get(EscalationCaseModel, case_id)
                if row is None:
                    return None
                if row.assigned_professional_id in {None, professional_id}:
                    row.assigned_professional_id = professional_id
                    row.review_status = "assigned"
                    session.commit()
                consultation = session.get(ConsultationModel, row.consultation_id)
                if consultation is None:
                    return None
                return self._build_professional_case(row, consultation)

    def review_case(self, case_id: str, professional_id: str) -> ProfessionalCaseDetail | None:
        with trace_span("repository.review_case", case_id=case_id, professional_id=professional_id):
            with self.SessionLocal() as session:
                row = session.get(EscalationCaseModel, case_id)
                if row is None:
                    return None
                row.assigned_professional_id = professional_id
                row.review_status = "reviewed"
                row.reviewed_at = datetime.now(UTC)
                consultation = session.get(ConsultationModel, row.consultation_id)
                if consultation is None:
                    return None
                consultation.status = ConsultationStatus.REVIEWED.value
                session.commit()
                return self._build_professional_case(row, consultation)

    def replace_corpus(
        self,
        documents: list[CorpusDocumentRecord],
        chunks: list[CorpusChunkRecord],
        index_version: str,
        index_artifact_path: str,
        embedding_provider: str,
        embedding_model: str,
        corpus_version: str,
    ) -> RAGStatus:
        with self.SessionLocal() as session:
            session.query(CorpusChunkModel).delete()
            session.query(CorpusDocumentModel).delete()
            session.add_all(
                [
                    CorpusDocumentModel(
                        document_id=item.document_id,
                        title=item.title,
                        source_type=item.source_type,
                        source_uri=item.source_uri,
                        clinical_topic=item.clinical_topic,
                        audience=item.audience,
                        publication_or_revision_date=item.publication_or_revision_date,
                        curation_status=item.curation_status,
                        language=item.language,
                        license_or_usage_note=item.license_or_usage_note,
                        summary=item.summary,
                        content=item.content,
                        metadata_json=item.metadata,
                        corpus_version=corpus_version,
                        ingested_at=datetime.now(UTC),
                    )
                    for item in documents
                ]
            )
            session.flush()
            session.add_all(
                [
                    CorpusChunkModel(
                        chunk_id=item.chunk_id,
                        document_id=item.document_id,
                        chunk_index=item.chunk_index,
                        title=item.title,
                        content=item.content,
                        token_count=item.token_count,
                        metadata_json=item.metadata,
                    )
                    for item in chunks
                ]
            )
            session.add(
                RagIndexRunModel(
                    id=str(uuid4()),
                    corpus_version=corpus_version,
                    retrieval_version=index_version,
                    embedding_provider=embedding_provider,
                    embedding_model=embedding_model,
                    documents=len(documents),
                    chunks=len(chunks),
                    index_artifact_path=index_artifact_path,
                    built_at=datetime.now(UTC),
                )
            )
            session.commit()
        return self.get_rag_status() or RAGStatus(
            corpus_version=corpus_version,
            retrieval_version=index_version,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            documents=len(documents),
            chunks=len(chunks),
            index_version=index_version,
            index_artifact_path=index_artifact_path,
        )

    def get_rag_status(self) -> RAGStatus | None:
        with self.SessionLocal() as session:
            latest_run = session.scalar(select(RagIndexRunModel).order_by(RagIndexRunModel.built_at.desc()))
            if latest_run is None:
                return None
            return RAGStatus(
                corpus_version=latest_run.corpus_version,
                retrieval_version=latest_run.retrieval_version,
                embedding_provider=latest_run.embedding_provider,
                embedding_model=latest_run.embedding_model,
                documents=latest_run.documents,
                chunks=latest_run.chunks,
                index_version=latest_run.retrieval_version,
                index_artifact_path=latest_run.index_artifact_path,
            )

    def record_retrieval_trace(self, consultation_id: str | None, trace: RetrievalTrace) -> None:
        with self.SessionLocal() as session:
            session.add(
                RagRetrievalTraceModel(
                    id=str(uuid4()),
                    consultation_id=consultation_id,
                    query_text=trace.query_text,
                    query_terms=trace.query_terms,
                    retrieval_version=trace.retrieval_version,
                    embedding_provider=trace.embedding_provider,
                    embedding_model=trace.embedding_model,
                    corpus_version=trace.corpus_version,
                    index_version=trace.index_version,
                    top_k=trace.top_k,
                    candidates_considered=trace.candidates_considered,
                    evidence_sources_json=[item.model_dump(mode="json") for item in trace.evidence_sources],
                    created_at=datetime.now(UTC),
                )
            )
            session.commit()

    def record_audit_event(
        self,
        actor_user_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None,
        outcome: str,
        metadata: dict[str, object] | None = None,
    ) -> AuditEvent:
        with self.SessionLocal() as session:
            model = AuditEventModel(
                id=str(uuid4()),
                actor_user_id=actor_user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                outcome=outcome,
                metadata_json=metadata,
                created_at=datetime.now(UTC),
            )
            session.add(model)
            session.commit()
            return self._build_audit_event(model)

    def list_audit_events(self) -> list[AuditEvent]:
        with self.SessionLocal() as session:
            rows = session.scalars(select(AuditEventModel).order_by(AuditEventModel.created_at.asc())).all()
            return [self._build_audit_event(row) for row in rows]

    def _build_user(self, model: UserModel) -> UserRecord:
        return UserRecord(
            id=model.id,
            username=model.username,
            full_name=model.full_name,
            password_hash=model.password_hash,
            role=UserRole(model.role),
        )

    def _build_consultation(self, model: ConsultationModel) -> ConsultationRecord:
        triage_result = None
        if model.triage_result is not None:
            triage_result = TriageResult(
                severity=SeverityLevel(model.triage_result.severity),
                decision=model.triage_result.decision,
                rationale=model.triage_result.rationale,
                confidence=model.triage_result.confidence,
                prompt_version=model.triage_result.prompt_version,
            )
        recommendation = None
        if model.recommendation is not None:
            recommendation = Recommendation(
                summary=model.recommendation.summary,
                disclaimer=model.recommendation.disclaimer,
                evidence_sources=[
                    EvidenceSource(
                        id=item.id,
                        document_id=item.document_id,
                        chunk_id=item.chunk_id,
                        title=item.title,
                        source_type=item.source_type,
                        uri=item.uri,
                        snippet=item.snippet,
                        retrieval_score=item.retrieval_score,
                        rank=item.rank,
                        retrieval_method=item.retrieval_method,
                        match_rationale=item.match_rationale,
                        matched_terms=list(item.matched_terms),
                    )
                    for item in sorted(model.recommendation.evidence_sources, key=lambda source: source.rank)
                ],
                generated_at=model.recommendation.generated_at,
                retrieval_version=model.recommendation.retrieval_version,
                embedding_provider=model.recommendation.embedding_provider,
                embedding_model=model.recommendation.embedding_model,
                corpus_version=model.recommendation.corpus_version,
            )
        return ConsultationRecord(
            id=model.id,
            patient_user_id=model.patient_user_id,
            chief_complaint=model.chief_complaint,
            context_notes=model.context_notes,
            age_range=model.age_range,
            chronic_conditions=list(model.chronic_conditions),
            symptoms=[
                SymptomEntry(
                    id=item.id,
                    symptom=item.symptom,
                    duration=item.duration,
                    intensity=item.intensity,
                    notes=item.notes,
                )
                for item in model.symptoms
            ],
            status=ConsultationStatus(model.status),
            created_at=model.created_at,
            triage_result=triage_result,
            recommendation=recommendation,
        )

    def _build_professional_case(self, row: EscalationCaseModel, consultation: ConsultationModel) -> ProfessionalCaseDetail:
        consultation_record = self._build_consultation(consultation)
        assert consultation_record.triage_result is not None
        assert consultation_record.recommendation is not None
        return ProfessionalCaseDetail(
            id=row.id,
            consultation_id=row.consultation_id,
            assigned_professional_id=row.assigned_professional_id,
            review_status=row.review_status,
            reason=row.reason,
            created_at=row.created_at,
            reviewed_at=row.reviewed_at,
            triage_result=consultation_record.triage_result,
            recommendation=consultation_record.recommendation,
            consultation=consultation_record,
        )

    def _build_audit_event(self, row: AuditEventModel) -> AuditEvent:
        return AuditEvent(
            id=row.id,
            actor_user_id=row.actor_user_id,
            action=row.action,
            resource_type=row.resource_type,
            resource_id=row.resource_id,
            outcome=row.outcome,
            metadata=row.metadata_json,
            created_at=row.created_at,
        )
