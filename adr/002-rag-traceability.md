# ADR-002 - Uso de RAG como mecanismo principal de recomendacion trazable

- Estado: Aceptada
- Fecha: 2026-03-22

## Contexto

El estado del arte y el enfoque del proyecto priorizan precision clinica y trazabilidad por encima de generacion libre. Un LLM aislado no ofrece garantias suficientes de fundamentacion.

## Decision

Se adopta un pipeline RAG para recuperar evidencia clinica antes de construir la recomendacion final.

## Justificacion

- Permite enlazar cada respuesta con fuentes concretas.
- Reduce dependencia de memoria parametrica del modelo.
- Refuerza la narrativa academica del proyecto frente al atributo de calidad dominante.

## Consecuencias

- El valor del sistema dependera de la calidad del corpus clinico y de su curacion.
- La arquitectura debe registrar metadata de retrieval, no solo la salida final del modelo.
