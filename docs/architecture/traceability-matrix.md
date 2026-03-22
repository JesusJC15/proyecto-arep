# Matriz de trazabilidad

| Requisito | Componentes principales | Vista / artefacto | Seccion del articulo |
| --- | --- | --- | --- |
| RF-01 Autenticacion por roles | Frontend paciente, frontend profesional, auth module | `02-c4-container.mmd`, `03-backend-components.mmd` | Requisitos, Arquitectura del prototipo |
| RF-02 Registro de sintomas | Frontend paciente, API, consultations module | `02-c4-container.mmd`, `04-sequence-triage.mmd` | Alcance, Contratos API |
| RF-03 Caso clinico estructurado | API, consultations module, triage module | `03-backend-components.mmd`, `04-sequence-triage.mmd` | Arquitectura del prototipo |
| RF-04 Clasificacion de severidad | Triage module | `03-backend-components.mmd`, `04-sequence-triage.mmd` | Requisitos, Flujo principal |
| RF-05 Recuperacion de evidencia | RAG service, vector store, corpus clinico | `02-c4-container.mmd`, `04-sequence-triage.mmd` | Arquitectura general, Flujo principal |
| RF-06 Recomendacion fundamentada | RAG service, audit module | `03-backend-components.mmd`, `04-sequence-triage.mmd` | Trazabilidad clinica, Contratos API |
| RF-07 Escalamiento a profesional | Triage module, professional cases | `05-sequence-escalation.mmd` | Arquitectura del prototipo |
| RF-08 Revision profesional | Frontend profesional, professional cases | `01-c4-context.mmd`, `02-c4-container.mmd`, `05-sequence-escalation.mmd` | Alcance, Flujo principal |
| RNF-01 Trazabilidad | Audit module, evidence source, recommendation | `03-backend-components.mmd`, `07-data-model.mmd` | Trazabilidad clinica, Modelo de datos |
| RNF-06 Preparacion cloud | AWS deployment mapping | `06-aws-deployment.mmd` | Arquitectura general |
