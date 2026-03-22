# AREP - Segunda Entrega

Este repositorio contiene la segunda entrega del proyecto AREP para la materia de Arquitectura Empresarial y Transformacion Digital. La entrega traduce el estado del arte inicial en una propuesta tecnica completa para una plataforma inteligente de triaje medico general asistida por IA.

## Estructura

- `paper/`: articulo IEEE en LaTeX para la segunda entrega.
- `docs/architecture/`: diagramas editables, matriz de trazabilidad y documentacion de arquitectura.
- `adr/`: decisiones de arquitectura relevantes para el MVP y la solucion objetivo.
- `backend/`: base del prototipo con FastAPI y contratos minimos.
- `frontend/`: base del prototipo con React y vistas para paciente y profesional.
- `knowledge-base/`: corpus clinico inicial curado para el pipeline RAG del prototipo.

## Alcance de esta entrega

- Arquitectura general objetivo en AWS.
- Arquitectura del prototipo MVP local.
- Definicion de entidades, endpoints y flujo clinico principal.
- Esqueleto tecnico del sistema para evolucionar hacia la tercera entrega.

## Fuera de alcance

- Despliegue real en AWS.
- Integracion real con historia clinica via FHIR.
- Evaluacion cuantitativa formal del prototipo.
- Automatizacion completa del pipeline RAG en produccion.
