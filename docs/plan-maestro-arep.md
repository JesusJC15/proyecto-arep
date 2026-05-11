# Plan Maestro AREP

Este documento consolida, en un solo lugar, el estado actual del proyecto AREP, lo ya implementado, lo que falta y el paso a paso recomendado para llevarlo a un nivel sobresaliente de cierre academico, demo reproducible y proyeccion tecnica seria.

## 1. Objetivo general

Dejar AREP como un proyecto:

- tecnicamente coherente de extremo a extremo
- demostrable de forma estable
- defendible academicamente
- reproducible por terceros
- con una ruta clara hacia produccion real

## 2. Estado actual resumido

### 2.1 Lo que ya tenemos

- autenticacion con JWT firmado
- control por roles `patient` y `professional`
- flujo real de consulta, triage, recomendacion y escalamiento
- bandeja profesional con toma y cierre de casos
- persistencia SQL compatible con SQLite y Postgres
- auditoria basica y observabilidad minima
- pipeline RAG reproducible con:
  - corpus versionado
  - chunking
  - embeddings locales por defecto
  - ranking y score visibles
  - dataset de evaluacion minimo
- frontend conectado al backend real
- CI con pruebas backend, build frontend y E2E
- empaquetado final con `Docker Compose`
- runbook, guion de demo, blueprint AWS y slides HTML

### 2.2 Lo que aun NO es produccion real

- no hay despliegue real en AWS
- no hay validacion clinica formal
- no hay secrets manager real
- no hay hardening de seguridad de nivel productivo
- no hay vector store productivo
- no hay monitoreo cloud real
- no hay validacion con usuarios finales o profesionales de salud

## 3. Entregables actuales del repositorio

### 3.1 Operacion y demo

- [README.md](../README.md)
- [docs/guides/runbook-final.md](guides/runbook-final.md)
- [docs/guides/demo-script.md](guides/demo-script.md)
- [docs/guides/final-checklists.md](guides/final-checklists.md)
- [docker-compose.yml](../docker-compose.yml)

### 3.2 Backend y RAG

- [backend/app/main.py](../backend/app/main.py)
- [backend/app/services/rag_service.py](../backend/app/services/rag_service.py)
- [backend/app/services/embeddings.py](../backend/app/services/embeddings.py)
- [backend/app/repositories/sql_repository.py](../backend/app/repositories/sql_repository.py)
- [backend/tests/test_phase2_backend.py](../backend/tests/test_phase2_backend.py)

### 3.3 Corpus y evaluacion

- [knowledge-base/corpus-manifest.json](../knowledge-base/corpus-manifest.json)
- [knowledge-base/curation-policy.md](../knowledge-base/curation-policy.md)
- [knowledge-base/evaluation/rag-evaluation-dataset.json](../knowledge-base/evaluation/rag-evaluation-dataset.json)
- [docs/technical/rag-evaluation.md](technical/rag-evaluation.md)

### 3.4 Paquete academico

- [paper/main.tex](../paper/main.tex)
- [docs/architecture/README.md](architecture/README.md)
- [docs/presentation/index.html](presentation/index.html)
- [infra/aws/README.md](../infra/aws/README.md)

## 4. Prioridades finales reales

El orden recomendado final es:

1. estabilidad de ejecucion
2. consistencia tecnica entre backend, frontend y Compose
3. consistencia documental entre README, paper, diagramas y slides
4. calidad de demo
5. calidad academica
6. proyeccion cloud y ruta futura

## 5. Paso a paso completo

### Paso 1. Levantar el sistema oficial

Objetivo:
confirmar que la topologia final oficial funciona como se espera.

Acciones:

1. arrancar Docker Desktop o el daemon Docker
2. ubicarse en la raiz del proyecto
3. ejecutar:

```bash
docker compose up --build -d
```

4. validar:
   - `http://localhost:4173`
   - `http://localhost:8000/health`
   - `http://localhost:8000/ready`
   - `http://localhost:8000/rag/status`
   - `http://localhost:8000/metrics`
5. verificar que Postgres este saludable
6. confirmar que el backend construyo o cargo el indice RAG

Criterio de cierre:

- el frontend abre
- el backend responde
- `rag/status` devuelve corpus, chunks e indice

### Paso 2. Validar el flujo funcional completo

Objetivo:
garantizar que la demo principal es estable.

Acciones:

1. ingresar como `ana.patient / demo123`
2. crear una consulta
3. ejecutar triage
4. confirmar que la recomendacion muestra:
   - severidad
   - decision
   - score
   - rank
   - metodo de retrieval
   - razon de recuperacion
5. cambiar a `dr.suarez / demo123`
6. abrir la bandeja profesional
7. tomar el caso
8. marcarlo como revisado

Criterio de cierre:

- el flujo pasa sin errores manuales
- los estados cambian correctamente
- la evidencia es visible y consistente

### Paso 3. Ejecutar toda la validacion automatica

Objetivo:
confirmar que el estado del repo es estable antes de presentar o entregar.

Acciones backend:

```bash
cd backend
python -m pytest -q
```

Acciones frontend:

```bash
cd frontend
npm install
npm run build
npm run test:e2e
```

Acciones Compose:

```bash
docker compose config
```

Si Docker esta disponible:

```bash
docker compose up --build -d
docker compose down -v
```

Criterio de cierre:

- tests backend pasan
- build frontend pasa
- E2E pasa
- compose es valido

### Paso 4. Validar el RAG con foco academico

Objetivo:
confirmar que el RAG soporta el discurso tecnico del proyecto.

Acciones:

1. abrir [docs/technical/rag-evaluation.md](technical/rag-evaluation.md)
2. revisar el dataset en [knowledge-base/evaluation/rag-evaluation-dataset.json](../knowledge-base/evaluation/rag-evaluation-dataset.json)
3. confirmar las metricas actuales:
   - `top-1 = 2/3`
   - `top-k = 3/3`
4. revisar si el caso leve sigue siendo el punto mas debil
5. decidir si antes de sustentar conviene:
   - mejorar el ranking del caso leve
   - o simplemente explicitar esa limitacion en la presentacion

Criterio de cierre:

- el equipo sabe explicar como funciona el retrieval
- el equipo sabe explicar sus limites

### Paso 5. Revisar coherencia entre demo y narrativa

Objetivo:
evitar contradicciones durante la sustentacion.

Acciones:

1. contrastar:
   - [README.md](../README.md)
   - [paper/main.tex](../paper/main.tex)
   - [docs/architecture/README.md](architecture/README.md)
   - [docs/presentation/index.html](presentation/index.html)
2. confirmar que todos describen:
   - Compose como ejecucion oficial
   - Postgres como base de demo final
   - RAG local reproducible
   - AWS como proyeccion
3. eliminar cualquier afirmacion residual sobre:
   - repositorio en memoria
   - mocks en frontend
   - vector store ya desplegado
   - integracion FHIR activa

Criterio de cierre:

- no hay contradicciones visibles entre artefactos

### Paso 6. Cerrar el paquete de arquitectura

Objetivo:
dejar las vistas tecnicas listas para evaluacion y referencia.

Acciones:

1. revisar:
   - [docs/architecture/02-c4-container.mmd](architecture/02-c4-container.mmd)
   - [docs/architecture/03-backend-components.mmd](architecture/03-backend-components.mmd)
   - [docs/architecture/04-sequence-triage.mmd](architecture/04-sequence-triage.mmd)
   - [docs/architecture/05-sequence-escalation.mmd](architecture/05-sequence-escalation.mmd)
   - [docs/architecture/06-aws-deployment.mmd](architecture/06-aws-deployment.mmd)
   - [docs/architecture/07-data-model.mmd](architecture/07-data-model.mmd)
2. exportar a PNG o PDF si la sustentacion lo necesita
3. confirmar que el diagrama AWS coincide con el blueprint en `infra/aws`

Criterio de cierre:

- diagramas listos para insertar o mostrar

### Paso 7. Cerrar el paquete academico

Objetivo:
dejar el material formal listo para sustentar.

Acciones:

1. revisar el abstract, objetivos, arquitectura, resultados, limites y trabajo futuro en [paper/main.tex](../paper/main.tex)
2. confirmar que el paper menciona:
   - Docker Compose
   - RAG evaluable
   - corpus curado
   - metricas actuales
   - limites reales
3. incorporar, si hace falta, anexos o apendices con:
   - dataset RAG
   - trazabilidad
   - blueprint AWS
4. validar la presentacion HTML en [docs/presentation/index.html](presentation/index.html)
5. ensayar la sustentacion con ese deck

Criterio de cierre:

- paper y slides cuentan exactamente la misma historia

### Paso 8. Validar el blueprint AWS

Objetivo:
dejar clara la proyeccion seria del sistema.

Acciones:

1. revisar:
   - [infra/aws/README.md](../infra/aws/README.md)
   - [infra/aws/main.tf](../infra/aws/main.tf)
   - [infra/aws/variables.tf](../infra/aws/variables.tf)
   - [infra/aws/outputs.tf](../infra/aws/outputs.tf)
2. confirmar el mapeo:
   - frontend -> S3 + CloudFront
   - backend -> ECR + ECS Fargate
   - base -> RDS PostgreSQL
3. explicar que no es despliegue real, sino blueprint base ejecutable a futuro

Criterio de cierre:

- el blueprint se puede defender tecnicamente

### Paso 9. Preparar la demo final real

Objetivo:
reducir al minimo el riesgo durante la sustentacion.

Acciones:

1. usar [docs/guides/demo-script.md](guides/demo-script.md)
2. ensayar al menos dos veces el flujo completo
3. dejar abiertos:
   - app
   - `ready`
   - `rag/status`
   - logs backend si quieres respaldo tecnico
4. preparar comandos de contingencia
5. decidir si usaras:
   - un caso nuevo creado en vivo
   - o el caso semilla como respaldo

Criterio de cierre:

- el equipo puede ejecutar la demo sin improvisar

### Paso 10. Preparar el cierre tecnico final

Objetivo:
dejar claro que el proyecto no termina en la demo.

Acciones:

1. tener lista una explicacion corta de:
   - que ya esta resuelto
   - que falta para produccion real
   - que falta para validacion clinica
2. usar [docs/guides/final-checklists.md](guides/final-checklists.md) como referencia final
3. definir el roadmap post-entrega:
   - vector store productivo
   - secrets manager
   - despliegue AWS real
   - validacion con expertos
   - pruebas con usuarios

Criterio de cierre:

- el proyecto se ve completo, honesto y escalable

## 6. Lo que aun falta de verdad

Si el objetivo es decir que AREP esta "completamente terminado" para un cierre sobresaliente, aun faltan estas piezas:

### 6.1 Para produccion real

- secrets manager real
- despliegue AWS real
- CI/CD con promotion real
- observabilidad cloud
- vector store o `pgvector` productivo
- seguridad y compliance mas fuertes

### 6.2 Para validacion clinica seria

- revision de profesionales de salud
- validacion del corpus
- evaluacion de precision del triage
- evaluacion de retrieval con mas casos
- limites de seguridad clinica mejor definidos

### 6.3 Para evaluacion con usuarios

- pruebas de usabilidad
- accesibilidad mas profunda
- validacion de claridad de mensajes
- validacion del flujo paciente y profesional con usuarios reales

## 7. Checklist final de presentacion

- Docker funciona
- Compose levanta
- frontend abre
- backend responde
- `rag/status` responde
- demo ensayada
- logs listos
- runbook listo
- paper listo
- slides listas
- blueprint AWS listo
- limitaciones claras
- trabajo futuro claro

## 8. Recomendacion practica final

Si el tiempo es corto, el orden minimo de cierre recomendado es:

1. arrancar y validar Compose real
2. correr tests y E2E
3. ensayar la demo completa
4. revisar paper + slides + README en una sola sentada
5. revisar blueprint AWS y narrativa final
6. congelar el estado del repo para la entrega

## 9. Criterio de “listo”

AREP esta realmente listo para entrega final cuando:

- corre con `docker compose up --build -d`
- la demo pasa sin improvisacion
- la documentacion no se contradice
- el paper refleja exactamente lo que el repo demuestra
- el equipo puede explicar con claridad:
  - como funciona
  - por que es valioso
  - que evidencia lo respalda
  - cuales son sus limites
  - como evolucionaria a produccion
