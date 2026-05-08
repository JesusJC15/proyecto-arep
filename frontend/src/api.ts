import type {
  AuthResponse,
  ConsultationCreatePayload,
  ConsultationRecord,
  ProfessionalCaseDetail,
  ProfessionalCaseSummary,
  UserRole
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    let detail = "Ocurrio un error inesperado.";
    try {
      const payload = await response.json();
      detail = payload.detail ?? detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export function login(username: string, password: string, role: UserRole) {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password, role })
  });
}

export function readSession(token: string) {
  return request<AuthResponse["user"]>("/auth/session", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function createConsultation(token: string, payload: ConsultationCreatePayload) {
  return request<ConsultationRecord>("/consultations", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload)
  });
}

export function runTriage(token: string, consultationId: string) {
  return request<ConsultationRecord>(`/consultations/${consultationId}/triage`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function listProfessionalCases(token: string) {
  return request<ProfessionalCaseSummary[]>("/professional/cases", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function getProfessionalCase(token: string, caseId: string) {
  return request<ProfessionalCaseDetail>(`/professional/cases/${caseId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function assignProfessionalCase(token: string, caseId: string) {
  return request<ProfessionalCaseDetail>(`/professional/cases/${caseId}/assign`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });
}

export function reviewProfessionalCase(token: string, caseId: string) {
  return request<ProfessionalCaseDetail>(`/professional/cases/${caseId}/review`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` }
  });
}
