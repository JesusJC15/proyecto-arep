export type UserRole = "patient" | "professional";
export type Severity = "low" | "medium" | "high";
export type ConsultationStatus = "submitted" | "recommended" | "escalated" | "reviewed";
export type ProfessionalReviewStatus = "pending" | "assigned" | "reviewed";
export type TriageDecision = "self_care" | "watch_and_wait" | "professional_review";

export interface ApiContract {
  method: "GET" | "POST";
  path: string;
  purpose: string;
}

export interface UserSummary {
  id: string;
  username: string;
  full_name: string;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserSummary;
}

export interface SymptomEntryInput {
  symptom: string;
  duration: string;
  intensity: Severity;
  notes?: string | null;
}

export interface ConsultationCreatePayload {
  chief_complaint: string;
  context_notes: string;
  age_range: string;
  chronic_conditions: string[];
  symptoms: SymptomEntryInput[];
}

export interface SymptomEntry extends SymptomEntryInput {
  id: string;
}

export interface EvidenceSource {
  id: string;
  document_id: string;
  chunk_id: string;
  title: string;
  source_type: string;
  uri: string;
  snippet: string;
  retrieval_score: number;
  rank: number;
  retrieval_method: string;
  match_rationale: string;
  matched_terms: string[];
}

export interface TriageResult {
  severity: Severity;
  decision: TriageDecision;
  rationale: string;
  confidence: number;
  prompt_version: string;
}

export interface Recommendation {
  summary: string;
  disclaimer: string;
  evidence_sources: EvidenceSource[];
  generated_at: string;
  retrieval_version: string;
  embedding_provider: string;
  embedding_model: string;
  corpus_version: string;
}

export interface ConsultationRecord {
  id: string;
  patient_user_id: string;
  chief_complaint: string;
  context_notes: string;
  age_range: string;
  chronic_conditions: string[];
  symptoms: SymptomEntry[];
  status: ConsultationStatus;
  created_at: string;
  triage_result: TriageResult | null;
  recommendation: Recommendation | null;
}

export interface ProfessionalCaseSummary {
  id: string;
  consultation_id: string;
  severity: Severity;
  review_status: ProfessionalReviewStatus;
  reason: string;
  created_at: string;
}

export interface ProfessionalCaseDetail {
  id: string;
  consultation_id: string;
  assigned_professional_id: string | null;
  review_status: ProfessionalReviewStatus;
  reason: string;
  created_at: string;
  reviewed_at: string | null;
  triage_result: TriageResult;
  recommendation: Recommendation;
  consultation: ConsultationRecord;
}
