import type { ApiContract } from "../types";

const apiContracts: ApiContract[] = [
  { method: "POST", path: "/auth/login", purpose: "Autenticar paciente o profesional con JWT firmado." },
  { method: "POST", path: "/consultations", purpose: "Registrar una consulta estructurada desde el portal del paciente." },
  { method: "POST", path: "/consultations/{id}/triage", purpose: "Ejecutar triage, obtener recomendacion y crear escalamiento si aplica." },
  { method: "GET", path: "/consultations/{id}/recommendation", purpose: "Consultar recomendacion con ranking, score y trazabilidad RAG." },
  { method: "GET", path: "/professional/cases", purpose: "Listar la bandeja real de casos escalados." },
  { method: "GET", path: "/professional/cases/{id}", purpose: "Consultar el detalle completo del caso." },
  { method: "POST", path: "/professional/cases/{id}/assign", purpose: "Tomar un caso para revision profesional." },
  { method: "POST", path: "/professional/cases/{id}/review", purpose: "Marcar un caso como revisado." },
  { method: "GET", path: "/rag/status", purpose: "Inspeccionar estado del corpus, embeddings e indice reproducible." }
];

const buildingBlocks = [
  {
    title: "Canal paciente",
    description: "Formulario real para sintomas, contexto y ejecucion de triage sobre la API."
  },
  {
    title: "Canal profesional",
    description: "Bandeja persistida en SQLite para tomar, revisar y cerrar casos escalados."
  },
  {
    title: "Backend FastAPI",
    description: "JWT, auditoria persistida, triage por reglas y pipeline RAG semantico trazable."
  },
  {
    title: "Corpus e indice local",
    description: "Corpus curado, chunking versionado, embeddings locales y artefacto reproducible."
  }
];

export function ArchitectureBrief() {
  return (
    <section className="workspace-grid">
      <article className="panel">
        <div className="eyebrow">Resumen tecnico</div>
        <h2>Arquitectura de la Fase 3</h2>
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
        <div className="eyebrow">Contratos API</div>
        <h2>Capacidades activas de la demo</h2>
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
