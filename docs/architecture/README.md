# Diagramas de Arquitectura

Este directorio contiene las vistas editables del proyecto AREP. Todas las vistas se mantienen en formato Mermaid para facilitar edicion, trazabilidad y exportacion posterior.

## Archivos

- `01-c4-context.mmd`
- `02-c4-container.mmd`
- `03-backend-components.mmd`
- `04-sequence-triage.mmd`
- `05-sequence-escalation.mmd`
- `06-aws-deployment.mmd`
- `07-data-model.mmd`
- `traceability-matrix.md`

## Recomendacion de uso

1. Revisar primero el contexto y contenedores.
2. Alinear los diagramas con el articulo en `paper/main.tex`.
3. Contrastar los diagramas con `docs/rag-evaluation.md` y `knowledge-base/corpus-manifest.json`.
4. Contrastar la proyeccion cloud con `infra/aws/README.md` y el `docker-compose.yml` oficial.
5. Exportar a PNG o PDF con Mermaid CLI si se requiere insertar figuras en una version final del articulo.

## Convenciones

- `patient` y `professional` son los unicos roles del MVP.
- `FHIR Adapter` se mantiene como componente futuro, no implementado.
- `RAG Service` ya representa un pipeline real con corpus curado, chunking, embeddings locales e indice reproducible.
