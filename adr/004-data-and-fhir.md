# ADR-004 - Persistencia relacional con capacidad vectorial y adaptador FHIR conceptual

- Estado: Aceptada
- Fecha: 2026-03-22

## Contexto

El MVP necesita modelar consultas, usuarios y resultados clinicos de forma transaccional, pero tambien debe soportar retrieval semantico sobre documentos curados. Ademas, el proyecto debe mostrar una ruta de interoperabilidad realista.

## Decision

Se adopta PostgreSQL como base operativa, con capacidad vectorial planificada para el prototipo, y se modela una capa futura de interoperabilidad basada en HL7 FHIR.

## Justificacion

- PostgreSQL cubre bien la necesidad transaccional del MVP.
- La estrategia vectorial evita introducir un almacen adicional temprano si no es necesario.
- FHIR permite hablar de interoperabilidad sin falsear una integracion no implementada.

## Consecuencias

- El prototipo local puede iniciar con repositorios simples mientras se conserva el contrato para una migracion posterior a `pgvector`.
- La historia clinica real queda explicitamente fuera de alcance en la segunda entrega.
