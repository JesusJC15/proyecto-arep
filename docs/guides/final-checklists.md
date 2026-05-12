# Final Checklists AREP

Checklist final para asegurar que la entrega y la demo no tengan sorpresas.

## Antes de la demo

- `docker compose up --build -d` completo.
- `docker compose ps` muestra backend, frontend y Postgres saludables.
- `http://localhost:4173` abre correctamente.
- `http://localhost:8000/health` responde `ok`.
- `http://localhost:8000/ready` responde `ready`.
- `http://localhost:8000/rag/status` devuelve corpus, chunks e indice.
- Credenciales demo probadas.
- Navegador con dos sesiones listas: paciente y profesional.

## Durante la demo

- Mostrar primero el problema y la arquitectura.
- Ejecutar el flujo de paciente de extremo a extremo.
- Enseñar la evidencia RAG recuperada.
- Cambiar al flujo del profesional.
- Cerrar el caso y confirmar que el estado cambia.

## Antes de entregar

- Revisar [README.md](../../README.md).
- Revisar [docs/TOC.md](../TOC.md).
- Revisar [docs/technical/API_REFERENCE.md](../technical/API_REFERENCE.md).
- Revisar [docs/technical/rag-evaluation.md](../technical/rag-evaluation.md).
- Revisar [docs/architecture/README.md](../architecture/README.md).
- Revisar [infra/aws/README.md](../../infra/aws/README.md).
- Revisar [docs/presentation/index.html](../presentation/index.html).

## Señales de alerta

- El backend arranca pero `ready` falla.
- El frontend carga pero no autentica.
- `rag/status` no coincide con el corpus esperado.
- Los enlaces en la documentacion apuntan a rutas inexistentes.

## Criterio de cierre

- La demo se puede repetir desde cero.
- La documentacion principal coincide con el repo.
- Los artefactos academicos y tecnicos cuentan la misma historia.