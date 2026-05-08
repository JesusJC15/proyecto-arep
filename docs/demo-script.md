# Guion de demo final AREP

## Objetivo

Mostrar en 5 a 8 minutos un flujo completo de triaje con evidencia trazable, escalamiento profesional y cierre del caso.

## Preparacion previa

- Levantar el sistema con `docker compose up --build -d`
- Verificar:
  - `http://localhost:4173`
  - `http://localhost:8000/ready`
  - `http://localhost:8000/rag/status`
- Tener abiertos:
  - la aplicacion
  - `rag/status`
  - `metrics` o logs del backend como respaldo tecnico

## Guion sugerido

### 1. Contexto rapido

- Explicar que AREP es una plataforma de triaje academica con:
  - autenticacion por roles
  - triage por reglas
  - RAG trazable
  - bandeja profesional

### 2. Flujo paciente

- Entrar como `ana.patient / demo123`
- Mostrar el formulario estructurado
- Ejecutar la consulta
- Enfatizar:
  - severidad
  - decision
  - evidencia con score y rank
  - version del pipeline RAG y corpus

### 3. Trazabilidad

- Mostrar que cada fuente tiene:
  - score
  - metodo
  - terminos coincidentes
  - razon de recuperacion
- Abrir `rag/status` para demostrar corpus e indice activos

### 4. Flujo profesional

- Cambiar a `dr.suarez / demo123`
- Mostrar el caso escalado
- Tomar el caso
- Marcarlo como revisado

### 5. Cierre tecnico

- Mencionar:
  - Compose reproducible
  - Postgres como base oficial de demo
  - health, ready, metrics y rag/status
  - dataset minimo de evaluacion RAG

## Contingencias

### Si el flujo paciente falla

- Reiniciar con `docker compose down -v && docker compose up --build -d`

### Si no aparece un caso nuevo

- Usar el caso semilla profesional

### Si falla el indice RAG

- Reforzar con `rag/status`
- Ejecutar reconstruccion del indice

### Si falla la UI

- Mostrar `metrics`, `ready` y logs del backend como respaldo de funcionamiento
