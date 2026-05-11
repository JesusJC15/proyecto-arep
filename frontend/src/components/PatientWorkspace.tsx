import { useMemo, useState } from "react";

import { buildSourceUrl, createConsultation, runTriage } from "../api";
import type { ConsultationRecord, Severity, UserSummary } from "../types";

interface PatientWorkspaceProps {
  token: string;
  user: UserSummary;
}

interface SymptomDraft {
  symptom: string;
  duration: string;
  intensity: Severity;
  notes: string;
}

const defaultSymptoms: SymptomDraft[] = [
  {
    symptom: "Molestia en el pecho",
    duration: "24h",
    intensity: "high",
    notes: "Intermitente y empeora con esfuerzo leve"
  }
];

export function PatientWorkspace({ token, user }: PatientWorkspaceProps) {
  const [chiefComplaint, setChiefComplaint] = useState("Molestia en el pecho y fatiga persistente");
  const [contextNotes, setContextNotes] = useState("Los sintomas empeoraron durante las ultimas 24 horas.");
  const [ageRange, setAgeRange] = useState("adult");
  const [chronicConditionsText, setChronicConditionsText] = useState("hypertension");
  const [symptoms, setSymptoms] = useState<SymptomDraft[]>(defaultSymptoms);
  const [consultation, setConsultation] = useState<ConsultationRecord | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const chronicConditions = useMemo(
    () =>
      chronicConditionsText
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    [chronicConditionsText]
  );

  function updateSymptom(index: number, field: keyof SymptomDraft, value: string) {
    setSymptoms((current) =>
      current.map((item, itemIndex) => (itemIndex === index ? { ...item, [field]: value } : item))
    );
  }

  function addSymptom() {
    setSymptoms((current) => [
      ...current,
      { symptom: "", duration: "", intensity: "low", notes: "" }
    ]);
  }

  function removeSymptom(index: number) {
    setSymptoms((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  async function handleSubmit() {
    setIsSubmitting(true);
    setError(null);
    setMessage(null);

    try {
      const created = await createConsultation(token, {
        chief_complaint: chiefComplaint,
        context_notes: contextNotes,
        age_range: ageRange,
        chronic_conditions: chronicConditions,
        symptoms: symptoms.map((item) => ({
          symptom: item.symptom,
          duration: item.duration,
          intensity: item.intensity,
          notes: item.notes || null
        }))
      });
      const triaged = await runTriage(token, created.id);
      setConsultation(triaged);
      setMessage(
        triaged.status === "escalated"
          ? "La consulta fue enviada y escalada automaticamente al espacio profesional."
          : "La consulta fue enviada y el triage genero una recomendacion inmediata."
      );
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "No fue posible procesar la consulta.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-grid">
      <article className="panel panel-highlight">
        <div className="eyebrow">Portal del paciente</div>
        <h2>Captura estructurada de sintomas</h2>
        <p className="muted">
          Sesion activa de <strong>{user.full_name}</strong>. Este formulario usa el contrato real del backend.
        </p>

        <div className="field-grid">
          <label>
            Motivo principal
            <input value={chiefComplaint} onChange={(event) => setChiefComplaint(event.target.value)} />
          </label>
          <label>
            Rango de edad
            <select value={ageRange} onChange={(event) => setAgeRange(event.target.value)}>
              <option value="adult">Adulto</option>
              <option value="adolescent">Adolescente</option>
              <option value="older_adult">Adulto mayor</option>
            </select>
          </label>
          <label className="field-span">
            Notas de contexto
            <textarea
              rows={4}
              value={contextNotes}
              onChange={(event) => setContextNotes(event.target.value)}
            />
          </label>
          <label className="field-span">
            Condiciones cronicas (separadas por coma)
            <input
              value={chronicConditionsText}
              onChange={(event) => setChronicConditionsText(event.target.value)}
            />
          </label>
        </div>

        <div className="section-header">
          <h3>Sintomas reportados</h3>
          <button type="button" className="ghost-button" onClick={addSymptom}>
            Agregar sintoma
          </button>
        </div>
        <div className="stacked-list">
          {symptoms.map((item, index) => (
            <div key={`${item.symptom}-${index}`} className="symptom-editor">
              <div className="field-grid compact-grid">
                <label>
                  Sintoma
                  <input value={item.symptom} onChange={(event) => updateSymptom(index, "symptom", event.target.value)} />
                </label>
                <label>
                  Duracion
                  <input value={item.duration} onChange={(event) => updateSymptom(index, "duration", event.target.value)} />
                </label>
                <label>
                  Intensidad
                  <select
                    value={item.intensity}
                    onChange={(event) => updateSymptom(index, "intensity", event.target.value)}
                  >
                    <option value="low">Baja</option>
                    <option value="medium">Media</option>
                    <option value="high">Alta</option>
                  </select>
                </label>
                <label>
                  Notas
                  <input value={item.notes} onChange={(event) => updateSymptom(index, "notes", event.target.value)} />
                </label>
              </div>
              {symptoms.length > 1 && (
                <button type="button" className="text-button" onClick={() => removeSymptom(index)}>
                  Eliminar sintoma
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="actions-row">
          <button type="button" className="primary-button" onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? "Procesando..." : "Enviar consulta y ejecutar triage"}
          </button>
        </div>

        {message && <div className="notice success-notice">{message}</div>}
        {error && <div className="notice error-notice">{error}</div>}
      </article>

      <article className="panel">
        <div className="eyebrow">Resultado trazable</div>
        <h2>Recomendacion y evidencia</h2>
        {!consultation ? (
          <p className="muted">
            Cuando ejecutes el flujo, aqui aparecera la recomendacion real generada por el backend.
          </p>
        ) : (
          <>
            <div className="panel-header">
              <div>
                <p className="muted">Consulta {consultation.id}</p>
                <h3>{consultation.chief_complaint}</h3>
              </div>
              {consultation.triage_result && (
                <span className={`badge badge-${consultation.triage_result.severity}`}>
                  {consultation.triage_result.severity}
                </span>
              )}
            </div>
            <div className="callout">
              <strong>Estado de la consulta</strong>
              <span>{consultation.status}</span>
            </div>
            {consultation.triage_result && (
              <div className="details-card">
                <p><strong>Decision:</strong> {consultation.triage_result.decision}</p>
                <p><strong>Justificacion:</strong> {consultation.triage_result.rationale}</p>
                <p><strong>Confianza:</strong> {(consultation.triage_result.confidence * 100).toFixed(0)}%</p>
              </div>
            )}
            {consultation.recommendation && (
              <>
                <p>{consultation.recommendation.summary}</p>
                <p className="muted">{consultation.recommendation.disclaimer}</p>
                <div className="details-card">
                  <p><strong>Pipeline RAG:</strong> {consultation.recommendation.retrieval_version}</p>
                  <p><strong>Proveedor de embeddings:</strong> {consultation.recommendation.embedding_provider}</p>
                  <p><strong>Modelo:</strong> {consultation.recommendation.embedding_model}</p>
                  <p><strong>Version del corpus:</strong> {consultation.recommendation.corpus_version}</p>
                </div>
                <div className="evidence-list">
                  {consultation.recommendation.evidence_sources.map((source) => (
                    <article key={source.id} className="evidence-card">
                      <h3>#{source.rank} {source.title}</h3>
                      <p className="muted">
                        Score {source.retrieval_score.toFixed(3)} · Metodo {source.retrieval_method}
                      </p>
                      <p>{source.snippet}</p>
                      <p className="muted">{source.match_rationale}</p>
                      {source.matched_terms.length > 0 && (
                        <p className="muted">Terminos coincidentes: {source.matched_terms.join(", ")}</p>
                      )}
                      <a href={buildSourceUrl(source.uri)} target="_blank" rel="noreferrer">
                        Ver fuente
                      </a>
                    </article>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </article>
    </section>
  );
}
