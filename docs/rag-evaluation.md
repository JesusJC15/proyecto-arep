# Evaluacion minima del RAG - Fase 3

## Dataset

El conjunto de referencia se encuentra en `knowledge-base/evaluation/rag-evaluation-dataset.json` y cubre tres escenarios:

- caso respiratorio moderado para `watch_and_wait`
- caso cardiorrespiratorio severo para `professional_review`
- caso leve para `self_care`

## Metricas actuales

- `top-1 hit`: `2/3`
- `top-k hit`: `3/3`

## Lectura

El pipeline ya recupera al menos una fuente esperada en todos los casos del dataset. El principal margen de mejora esta en el escenario leve, donde la fuente mas pertinente todavia no siempre aparece en el primer puesto.

## Limites

- dataset pequeno y orientado a demo
- sin evaluacion clinica formal
- sin benchmark frente a proveedor externo de embeddings
