export type Severity = "low" | "medium" | "high";

export interface EvidenceSource {
  id: string;
  title: string;
  snippet: string;
}

export interface RecommendationPreview {
  severity: Severity;
  decision: "self_care" | "watch_and_wait" | "professional_review";
  summary: string;
  disclaimer: string;
  sources: EvidenceSource[];
}

export interface ConsultationDraft {
  patientName: string;
  chiefComplaint: string;
  symptoms: string[];
  contextNotes: string;
}

export interface ProfessionalCase {
  id: string;
  patientAlias: string;
  severity: Severity;
  reason: string;
  recommendation: string;
  evidenceTitles: string[];
}

export interface ApiContract {
  method: "GET" | "POST";
  path: string;
  purpose: string;
}
