# Evaluacion minima del RAG - Fase 3

El conjunto de referencia se encuentra en [knowledge-base/evaluation/rag-evaluation-dataset.json](../../knowledge-base/evaluation/rag-evaluation-dataset.json).

## Objetivo

Validar que el servicio de recuperacion trae evidencia util, trazable y consistente para el flujo de triaje.

## Metricas actuales

- `top-1 hit`: `2/3`
- `top-k hit`: `3/3`

## Lectura de resultados

- `top-1 hit` mide si la mejor fuente recuperada coincide con la esperada.
- `top-k hit` mide si la respuesta correcta aparece dentro del grupo recuperado por el sistema.

## Interpretacion

- El sistema cumple el objetivo minimo de cobertura dentro del conjunto de referencia.
- El caso mas debil sigue siendo el mas leve, por lo que debe explicarse como limitacion metodologica, no como validacion clinica formal.

## Reproduccion

1. Revisar el corpus curado en `knowledge-base/clinical-guidelines/`.
2. Revisar el indice sintetizado en `artifacts/rag-index.json`.
3. Ejecutar la API y consultar `GET /rag/status` para confirmar corpus e indice cargados.
4. Consultar `GET /rag/source?uri=...` para inspeccionar el origen textual de una evidencia concreta.

## Limitaciones

- Dataset pequeno.
- Sin validacion clinica formal.
- Orientado a demostracion academica y trazabilidad del prototipo.
