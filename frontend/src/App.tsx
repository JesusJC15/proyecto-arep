import { useEffect, useMemo, useState } from "react";

import { login, readSession } from "./api";
import { ArchitectureBrief } from "./components/ArchitectureBrief";
import { PatientWorkspace } from "./components/PatientWorkspace";
import { ProfessionalWorkspace } from "./components/ProfessionalWorkspace";
import type { AuthResponse, UserRole } from "./types";

type ViewMode = "patient" | "professional" | "architecture";

const tabs: Array<{ id: ViewMode; label: string; caption: string }> = [
  {
    id: "patient",
    label: "Portal paciente",
    caption: "Registro real de sintomas, triage y recomendacion con evidencia."
  },
  {
    id: "professional",
    label: "Espacio profesional",
    caption: "Casos escalados persistidos y acciones reales de revision."
  },
  {
    id: "architecture",
    label: "Arquitectura",
    caption: "Resumen de contratos y bloques tecnicos de la demo."
  }
];

const STORAGE_KEY = "arep-demo-session";

export default function App() {
  const [activeView, setActiveView] = useState<ViewMode>("patient");
  const [username, setUsername] = useState("ana.patient");
  const [password, setPassword] = useState("demo123");
  const [role, setRole] = useState<UserRole>("patient");
  const [session, setSession] = useState<AuthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  useEffect(() => {
    const rawSession = localStorage.getItem(STORAGE_KEY);
    if (rawSession) {
      try {
        const parsed = JSON.parse(rawSession) as AuthResponse;
        void (async () => {
          try {
            const user = await readSession(parsed.access_token);
            const nextSession = { ...parsed, user };
            setSession(nextSession);
            setActiveView(user.role === "professional" ? "professional" : "patient");
          } catch {
            localStorage.removeItem(STORAGE_KEY);
            setSession(null);
          }
        })();
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  useEffect(() => {
    if (session) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [session]);

  const sessionLabel = useMemo(() => {
    if (!session) {
      return "Sin sesion activa";
    }
    return `${session.user.full_name} · ${session.user.role}`;
  }, [session]);

  async function handleLogin(selectedUsername = username, selectedPassword = password, selectedRole = role) {
    setIsLoggingIn(true);
    setError(null);
    try {
      const nextSession = await login(selectedUsername, selectedPassword, selectedRole);
      setSession(nextSession);
      setRole(selectedRole);
      setUsername(selectedUsername);
      setPassword(selectedPassword);
      setActiveView(selectedRole === "professional" ? "professional" : "patient");
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : "No fue posible iniciar sesion.");
    } finally {
      setIsLoggingIn(false);
    }
  }

  function handleDemoLogin(selectedRole: UserRole) {
    const credentials =
      selectedRole === "patient"
        ? { username: "ana.patient", password: "demo123" }
        : { username: "dr.suarez", password: "demo123" };
    void handleLogin(credentials.username, credentials.password, selectedRole);
  }

  function handleLogout() {
    setSession(null);
    setError(null);
    setActiveView("patient");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <p className="sidebar-kicker">AREP fase 3</p>
        <h1>Plataforma inteligente de triage</h1>
        <p className="sidebar-text">
          RAG creible con corpus curado, retrieval trazable, auditoria y flujo profesional.
        </p>
        <div className="session-card">
          <strong>{sessionLabel}</strong>
          {session && (
            <button type="button" className="text-button" onClick={handleLogout}>
              Cerrar sesion
            </button>
          )}
        </div>
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
            <p className="eyebrow">Flujo E2E endurecido</p>
            <h2>JWT real, retrieval semantico local, corpus versionado y trazabilidad visible</h2>
          </div>
          <div className="hero-metrics">
            <div>
              <span>Roles</span>
              <strong>2</strong>
            </div>
            <div>
              <span>Endpoints</span>
              <strong>9</strong>
            </div>
            <div>
              <span>Flujo</span>
              <strong>RAG trazable</strong>
            </div>
          </div>
        </header>

        <section className="panel login-panel">
          <div className="eyebrow">Acceso</div>
          <div className="login-grid">
            <label>
              Usuario
              <input value={username} onChange={(event) => setUsername(event.target.value)} />
            </label>
            <label>
              Contrasena
              <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
            </label>
            <label>
              Rol
              <select value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
                <option value="patient">Paciente</option>
                <option value="professional">Profesional</option>
              </select>
            </label>
            <div className="actions-row">
              <button
                type="button"
                className="primary-button"
                onClick={() => void handleLogin()}
                disabled={isLoggingIn}
              >
                {isLoggingIn ? "Ingresando..." : "Ingresar"}
              </button>
              <button type="button" className="ghost-button" onClick={() => handleDemoLogin("patient")}>
                Demo paciente
              </button>
              <button type="button" className="ghost-button" onClick={() => handleDemoLogin("professional")}>
                Demo profesional
              </button>
            </div>
          </div>
          {error && <div className="notice error-notice">{error}</div>}
        </section>

        {activeView === "patient" && session?.user.role === "patient" && (
          <PatientWorkspace token={session.access_token} user={session.user} />
        )}
        {activeView === "patient" && session?.user.role !== "patient" && (
          <section className="panel">
            <p className="muted">Inicia sesion como paciente para usar el flujo de consulta real.</p>
          </section>
        )}
        {activeView === "professional" && session?.user.role === "professional" && (
          <ProfessionalWorkspace token={session.access_token} user={session.user} />
        )}
        {activeView === "professional" && session?.user.role !== "professional" && (
          <section className="panel">
            <p className="muted">Inicia sesion como profesional para acceder a la bandeja real de casos.</p>
          </section>
        )}
        {activeView === "architecture" && <ArchitectureBrief />}
      </main>
    </div>
  );
}
