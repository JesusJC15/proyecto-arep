import type { ApiContract, ProfessionalCase, RecommendationPreview } from "./types";

export const apiContracts: ApiContract[] = [
  { method: "POST", path: "/auth/login", purpose: "Authenticate patient or professional user" },
  { method: "POST", path: "/consultations", purpose: "Create a new consultation from symptom intake" },
  { method: "GET", path: "/consultations/{id}", purpose: "Retrieve consultation state and outputs" },
  { method: "POST", path: "/consultations/{id}/triage", purpose: "Run triage and grounded recommendation" },
  { method: "GET", path: "/consultations/{id}/recommendation", purpose: "Read grounded recommendation and evidence" },
  { method: "GET", path: "/professional/cases", purpose: "List escalated cases for review" },
  { method: "GET", path: "/professional/cases/{id}", purpose: "Read detailed escalated case" }
];

export const recommendationPreview: RecommendationPreview = {
  severity: "high",
  decision: "professional_review",
  summary:
    "The consultation should be escalated to a clinician because the reported pattern includes high-intensity symptoms and a potential red-flag trajectory.",
  disclaimer:
    "Academic prototype only. This experience illustrates the intended behavior of the MVP and does not replace a clinician.",
  sources: [
    {
      id: "src-1",
      title: "Red Flags for Escalation",
      snippet: "High intensity symptoms, uncertainty or rapid worsening trigger professional review."
    },
    {
      id: "src-2",
      title: "General Triage Guidance",
      snippet: "Store the justification used to classify severity and preserve traceability."
    }
  ]
};

export const professionalCases: ProfessionalCase[] = [
  {
    id: "case-001",
    patientAlias: "Patient AT-01",
    severity: "high",
    reason: "High severity or low confidence recommendation",
    recommendation:
      "Escalate to professional review and keep the evidence trace attached to the generated guidance.",
    evidenceTitles: ["Red Flags for Escalation", "General Triage Guidance"]
  },
  {
    id: "case-002",
    patientAlias: "Patient LM-07",
    severity: "medium",
    reason: "Follow-up required due to persistent symptoms",
    recommendation:
      "Monitor closely and schedule early clinical follow-up if the symptom burden increases.",
    evidenceTitles: ["Self-care Boundaries", "General Triage Guidance"]
  }
];
