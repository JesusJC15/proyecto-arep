import { useState } from "react";

import { recommendationPreview } from "../mockData";
import type { ConsultationDraft } from "../types";

const defaultDraft: ConsultationDraft = {
  patientName: "Ana Torres",
  chiefComplaint: "Chest tightness and persistent fatigue",
  symptoms: ["Chest discomfort", "Fatigue", "Shortness of breath"],
  contextNotes: "Symptoms worsened over the last 24 hours after mild activity."
};

export function PatientWorkspace() {
  const [draft, setDraft] = useState(defaultDraft);

  return (
    <section className="workspace-grid">
      <article className="panel panel-highlight">
        <div className="eyebrow">Patient intake</div>
        <h2>Structured symptom capture</h2>
        <p className="muted">
          This screen represents the MVP flow where the patient creates a consultation before triage.
        </p>
        <div className="field-grid">
          <label>
            Patient
            <input
              value={draft.patientName}
              onChange={(event) => setDraft({ ...draft, patientName: event.target.value })}
            />
          </label>
          <label>
            Chief complaint
            <input
              value={draft.chiefComplaint}
              onChange={(event) => setDraft({ ...draft, chiefComplaint: event.target.value })}
            />
          </label>
          <label className="field-span">
            Context notes
            <textarea
              rows={5}
              value={draft.contextNotes}
              onChange={(event) => setDraft({ ...draft, contextNotes: event.target.value })}
            />
          </label>
        </div>
        <div className="chip-row">
          {draft.symptoms.map((symptom) => (
            <span key={symptom} className="chip">
              {symptom}
            </span>
          ))}
        </div>
        <div className="callout">
          <strong>Next backend action</strong>
          <span>`POST /consultations` followed by `POST /consultations/{'{id}'}/triage`</span>
        </div>
      </article>

      <article className="panel">
        <div className="eyebrow">Grounded output</div>
        <div className="panel-header">
          <h2>Recommendation preview</h2>
          <span className={`badge badge-${recommendationPreview.severity}`}>
            {recommendationPreview.severity}
          </span>
        </div>
        <p>{recommendationPreview.summary}</p>
        <p className="muted">{recommendationPreview.disclaimer}</p>
        <div className="evidence-list">
          {recommendationPreview.sources.map((source) => (
            <article key={source.id} className="evidence-card">
              <h3>{source.title}</h3>
              <p>{source.snippet}</p>
            </article>
          ))}
        </div>
      </article>
    </section>
  );
}
