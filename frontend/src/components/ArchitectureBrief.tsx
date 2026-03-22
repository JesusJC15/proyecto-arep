import { apiContracts } from "../mockData";

const buildingBlocks = [
  {
    title: "Patient channel",
    description: "React interface for symptom intake, consultation status and grounded recommendation."
  },
  {
    title: "Professional channel",
    description: "React dashboard for escalated cases with evidence trace and recommendation review."
  },
  {
    title: "FastAPI core",
    description: "Auth, consultations, triage orchestration, recommendation retrieval and professional cases."
  },
  {
    title: "Data and knowledge",
    description: "Operational persistence plus a vector-ready layer backed by a curated knowledge base."
  }
];

export function ArchitectureBrief() {
  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="eyebrow">Architecture brief</div>
        <h2>Reference solution</h2>
        <div className="stack-grid">
          {buildingBlocks.map((block) => (
            <article key={block.title} className="stack-card">
              <h3>{block.title}</h3>
              <p>{block.description}</p>
            </article>
          ))}
        </div>
      </article>

      <article className="panel">
        <div className="eyebrow">API blueprint</div>
        <h2>Contracts aligned with the MVP</h2>
        <div className="contracts">
          {apiContracts.map((contract) => (
            <div key={contract.path} className="contract-row">
              <span className="method">{contract.method}</span>
              <code>{contract.path}</code>
              <p>{contract.purpose}</p>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}
