# ADR-004 - Persistencia relacional, indice local reproducible y ruta futura a capacidad vectorial

- Estado: Aceptada
- Fecha: 2026-03-22

## Contexto

El MVP necesita modelar consultas, usuarios y resultados clinicos de forma transaccional, pero tambien debe soportar retrieval semantico sobre documentos curados. Ademas, el proyecto debe mostrar una ruta de interoperabilidad realista.

## Decision

Se adopta una estrategia en dos niveles: persistencia operativa en SQLite/PostgreSQL para entidades transaccionales y corpus/chunks, mas un indice semantico local reproducible como artefacto del prototipo. La ruta futura hacia `pgvector` se conserva como evolucion natural, y la interoperabilidad basada en HL7 FHIR permanece como capacidad conceptual no implementada.

## Justificacion

- PostgreSQL cubre bien la necesidad transaccional del MVP y SQLite simplifica la demo local.
- Un indice local reproducible permite demostrar retrieval semantico sin obligar una infraestructura vectorial gestionada temprana.
- FHIR permite hablar de interoperabilidad sin falsear una integracion no implementada.

## Consecuencias

- El prototipo local persiste documentos y chunks en SQL, y guarda embeddings en un artefacto reproducible fuera de la base transaccional.
- La migracion posterior a `pgvector` o un vector store gestionado no requiere redisenar los contratos del pipeline RAG.
- La historia clinica real queda explicitamente fuera de alcance en la segunda entrega.
