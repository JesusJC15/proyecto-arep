import { professionalCases } from "../mockData";

export function ProfessionalWorkspace() {
  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="eyebrow">Professional queue</div>
        <h2>Escalated cases</h2>
        <p className="muted">
          The professional dashboard consumes the escalated branch of the triage workflow.
        </p>
        <div className="case-list">
          {professionalCases.map((item) => (
            <article key={item.id} className="case-card">
              <div className="case-card-header">
                <div>
                  <strong>{item.patientAlias}</strong>
                  <p>{item.reason}</p>
                </div>
                <span className={`badge badge-${item.severity}`}>{item.severity}</span>
              </div>
              <p>{item.recommendation}</p>
              <div className="chip-row">
                {item.evidenceTitles.map((evidence) => (
                  <span key={evidence} className="chip chip-contrast">
                    {evidence}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </article>

      <article className="panel panel-highlight">
        <div className="eyebrow">Role intent</div>
        <h2>What the professional actually reviews</h2>
        <ul className="check-list">
          <li>Severity and decision produced by the triage module.</li>
          <li>Evidence sources used by the RAG workflow.</li>
          <li>Recommendation summary and disclaimer.</li>
          <li>Status transition from `escalated` to `reviewed` in future phases.</li>
        </ul>
      </article>
    </section>
  );
}
