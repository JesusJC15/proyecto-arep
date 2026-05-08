import { useEffect, useState } from "react";

import {
  assignProfessionalCase,
  getProfessionalCase,
  listProfessionalCases,
  reviewProfessionalCase
} from "../api";
import type { ProfessionalCaseDetail, ProfessionalCaseSummary, UserSummary } from "../types";

interface ProfessionalWorkspaceProps {
  token: string;
  user: UserSummary;
}

export function ProfessionalWorkspace({ token, user }: ProfessionalWorkspaceProps) {
  const [cases, setCases] = useState<ProfessionalCaseSummary[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [caseDetail, setCaseDetail] = useState<ProfessionalCaseDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function refreshCases(nextSelectedCaseId?: string | null) {
    setIsLoading(true);
    setError(null);
    try {
      const list = await listProfessionalCases(token);
      setCases(list);
      const resolvedCaseId = nextSelectedCaseId ?? selectedCaseId ?? list[0]?.id ?? null;
      setSelectedCaseId(resolvedCaseId);
      if (resolvedCaseId) {
        const detail = await getProfessionalCase(token, resolvedCaseId);
        setCaseDetail(detail);
      } else {
        setCaseDetail(null);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar la bandeja profesional.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshCases();
  }, []);

  useEffect(() => {
    if (!selectedCaseId) {
      return;
    }
    void (async () => {
      try {
        const detail = await getProfessionalCase(token, selectedCaseId);
        setCaseDetail(detail);
      } catch (detailError) {
        setError(detailError instanceof Error ? detailError.message : "No fue posible cargar el detalle del caso.");
      }
    })();
  }, [selectedCaseId, token]);

  async function handleAssign() {
    if (!selectedCaseId) {
      return;
    }
    setIsMutating(true);
    setMessage(null);
    setError(null);
    try {
      const detail = await assignProfessionalCase(token, selectedCaseId);
      setCaseDetail(detail);
      await refreshCases(selectedCaseId);
      setMessage("Caso asignado correctamente a la sesion profesional actual.");
    } catch (mutationError) {
      setError(mutationError instanceof Error ? mutationError.message : "No fue posible asignar el caso.");
    } finally {
      setIsMutating(false);
    }
  }

  async function handleReview() {
    if (!selectedCaseId) {
      return;
    }
    setIsMutating(true);
    setMessage(null);
    setError(null);
    try {
      const detail = await reviewProfessionalCase(token, selectedCaseId);
      setCaseDetail(detail);
      await refreshCases(selectedCaseId);
      setMessage("Caso marcado como revisado.");
    } catch (mutationError) {
      setError(mutationError instanceof Error ? mutationError.message : "No fue posible marcar el caso como revisado.");
    } finally {
      setIsMutating(false);
    }
  }

  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">Bandeja profesional</div>
            <h2>Casos escalados</h2>
          </div>
          <button type="button" className="ghost-button" onClick={() => void refreshCases()}>
            Actualizar
          </button>
        </div>
        <p className="muted">
          Sesion activa de <strong>{user.full_name}</strong>. El listado proviene de SQLite via backend real.
        </p>
        {isLoading ? (
          <p className="muted">Cargando casos...</p>
        ) : cases.length === 0 ? (
          <p className="muted">No hay casos escalados pendientes en este momento.</p>
        ) : (
          <div className="case-list">
            {cases.map((item) => (
              <button
                key={item.id}
                type="button"
                className={item.id === selectedCaseId ? "case-card case-card-active" : "case-card"}
                onClick={() => setSelectedCaseId(item.id)}
              >
                <div className="case-card-header">
                  <div>
                    <strong>{item.consultation_id}</strong>
                    <p>{item.reason}</p>
                  </div>
                  <span className={`badge badge-${item.severity}`}>{item.severity}</span>
                </div>
                <p className="muted">Estado: {item.review_status}</p>
              </button>
            ))}
          </div>
        )}
      </article>

      <article className="panel panel-highlight">
        <div className="eyebrow">Detalle del caso</div>
        <h2>Revision profesional</h2>
        {error && <div className="notice error-notice">{error}</div>}
        {message && <div className="notice success-notice">{message}</div>}
        {!caseDetail ? (
          <p className="muted">Selecciona un caso para revisar la consulta, la decision y la evidencia.</p>
        ) : (
          <>
            <div className="panel-header">
              <div>
                <p className="muted">Caso {caseDetail.id}</p>
                <h3>{caseDetail.consultation.chief_complaint}</h3>
              </div>
              <span className={`badge badge-${caseDetail.triage_result.severity}`}>
                {caseDetail.triage_result.severity}
              </span>
            </div>
            <div className="details-card">
              <p><strong>Estado:</strong> {caseDetail.review_status}</p>
              <p><strong>Profesional asignado:</strong> {caseDetail.assigned_professional_id ?? "Sin asignar"}</p>
              <p><strong>Decision:</strong> {caseDetail.triage_result.decision}</p>
              <p><strong>Razon de escalamiento:</strong> {caseDetail.reason}</p>
            </div>
            <div className="chip-row">
              {caseDetail.consultation.symptoms.map((symptom) => (
                <span key={symptom.id} className="chip chip-contrast">
                  {symptom.symptom} · {symptom.intensity}
                </span>
              ))}
            </div>
            <p>{caseDetail.recommendation.summary}</p>
            <div className="details-card">
              <p><strong>Pipeline RAG:</strong> {caseDetail.recommendation.retrieval_version}</p>
              <p><strong>Proveedor:</strong> {caseDetail.recommendation.embedding_provider}</p>
              <p><strong>Modelo:</strong> {caseDetail.recommendation.embedding_model}</p>
              <p><strong>Corpus:</strong> {caseDetail.recommendation.corpus_version}</p>
            </div>
            <div className="evidence-list">
              {caseDetail.recommendation.evidence_sources.map((source) => (
                <article key={source.id} className="evidence-card">
                  <h3>#{source.rank} {source.title}</h3>
                  <p className="muted">
                    Score {source.retrieval_score.toFixed(3)} · Metodo {source.retrieval_method}
                  </p>
                  <p>{source.snippet}</p>
                  <p className="muted">{source.match_rationale}</p>
                </article>
              ))}
            </div>
            <div className="actions-row">
              <button type="button" className="ghost-button" onClick={handleAssign} disabled={isMutating}>
                {isMutating ? "Procesando..." : "Tomar caso"}
              </button>
              <button type="button" className="primary-button" onClick={handleReview} disabled={isMutating}>
                {isMutating ? "Procesando..." : "Marcar revisado"}
              </button>
            </div>
          </>
        )}
      </article>
    </section>
  );
}
