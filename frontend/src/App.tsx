import { useState } from "react";

import { ArchitectureBrief } from "./components/ArchitectureBrief";
import { PatientWorkspace } from "./components/PatientWorkspace";
import { ProfessionalWorkspace } from "./components/ProfessionalWorkspace";

type ViewMode = "patient" | "professional" | "architecture";

const tabs: Array<{ id: ViewMode; label: string; caption: string }> = [
  {
    id: "patient",
    label: "Patient portal",
    caption: "Symptom intake, triage and grounded recommendation."
  },
  {
    id: "professional",
    label: "Professional desk",
    caption: "Escalated cases with evidence trace and review context."
  },
  {
    id: "architecture",
    label: "Architecture",
    caption: "Contracts and building blocks for the second delivery."
  }
];

export default function App() {
  const [activeView, setActiveView] = useState<ViewMode>("patient");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <p className="sidebar-kicker">AREP second delivery</p>
        <h1>Intelligent triage platform</h1>
        <p className="sidebar-text">
          Academic MVP for general medical triage with modular architecture, grounded generation and
          professional escalation.
        </p>
        <nav className="nav-list">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={tab.id === activeView ? "nav-button nav-button-active" : "nav-button"}
              onClick={() => setActiveView(tab.id)}
            >
              <strong>{tab.label}</strong>
              <span>{tab.caption}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="content">
        <header className="hero">
          <div>
            <p className="eyebrow">Precision and traceability first</p>
            <h2>Second delivery aligned with the article, diagrams and backend contracts</h2>
          </div>
          <div className="hero-metrics">
            <div>
              <span>Roles</span>
              <strong>2</strong>
            </div>
            <div>
              <span>Core endpoints</span>
              <strong>7</strong>
            </div>
            <div>
              <span>Primary flow</span>
              <strong>Triage</strong>
            </div>
          </div>
        </header>

        {activeView === "patient" && <PatientWorkspace />}
        {activeView === "professional" && <ProfessionalWorkspace />}
        {activeView === "architecture" && <ArchitectureBrief />}
      </main>
    </div>
  );
}
