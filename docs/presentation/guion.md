# Guion de exposición — AREP

Este documento contiene el guion sugerido para la exposición en equipo. Cada persona tiene su bloque con diapositivas sugeridas, mensaje central, puntos clave y preguntas probables.

---

## Guion general

- Persona 1: Contexto, problema, propuesta, stack y visión general de la arquitectura. (4–5 min)
- Persona 2: Diagramas técnicos, backend, RAG, APIs, frontend y pruebas/resultados. (5–6 min)
- Persona 3: Despliegue AWS, seguridad, métricas, límites, futuro y conclusión. (4–5 min)

---

## Persona 1 — Introducción y visión (Diapositivas 1–6)

**Diapositivas sugeridas:** título, narrativa, problema, solución, stack, visión general.

**Mensaje central:** Explicar por qué el problema importa, cómo AREP lo aborda y las decisiones técnicas principales.

**Puntos clave:**
- Triaje médico asistido por IA con trazabilidad.
- Separación clara entre paciente y profesional.
- Stack: FastAPI (backend), React + Vite (frontend), PostgreSQL (datos), Docker, AWS (despliegue).
- Decisiones orientadas a claridad, modularidad y evolución.

**Transición:** “Con el problema y la propuesta claros, ahora vemos cómo se materializa técnicamente en la arquitectura y en el flujo clínico.”

**Preguntas probables:**
- ¿Por qué usar RAG?
- ¿Por qué no un frontend más simple?
- ¿Qué hace que esto sea una entrega académica y no solo una demo?

---

## Persona 2 — Arquitectura y evidencia (Diapositivas ~7–14)

**Diapositivas sugeridas:** diagramas de contexto, contenedores, backend, datos, secuencias, UX, APIs y pruebas.

**Mensaje central:** Demostrar que la arquitectura y los endpoints están reflejados en el repositorio y en los diagramas.

**Puntos clave:**
- Explicar el flujo: intake → triage → recuperación de evidencia (RAG) → recomendación trazable → escalamiento.
- Mostrar trazabilidad: cada recomendación liga a fuentes y scores.
- Presentar métricas de evaluación del RAG con transparencia (top-1, top-k).
- Apoyarse en los diagramas PNG para evidenciar la arquitectura real.

**Transición:** “Ya vimos cómo funciona y cómo está construido; vamos a la parte de despliegue, seguridad y cierre.”

**Preguntas probables:**
- ¿Qué endpoint genera la recomendación?
- ¿Cómo se almacenan y referencian las fuentes?
- ¿Qué significan 2/3 y 3/3 en la evaluación?

---

## Persona 3 — Despliegue, seguridad y cierre (Diapositivas ~15–19)

**Diapositivas sugeridas:** AWS, calidad, seguridad, límites, futuro, conclusión.

**Mensaje central:** Mostrar que existe una vía de despliegue, una demo pública y una postura clara sobre límites y roadmap.

**Puntos clave:**
- Demo pública: frontend en S3 (URL incluida en la presentación).
- Blueprint para backend: ECS/ECR/RDS y Terraform en `infra/aws`.
- Seguridad y privacidad: JWT, roles, auditoría y rate limiting.
- Límites: no hay validación clínica formal; es una entrega académica reproducible.

**Transición final:** “Con esto cerramos la propuesta y dejamos abiertas las preguntas.”

**Preguntas probables:**
- ¿Qué falta para producción?
- ¿Cómo escalaría en AWS?
- ¿Qué harían distinto con más tiempo?

---

## Q&A breve (sugerencias para respuestas rápidas)

- ¿Por qué RAG y no un modelo generativo? — Porque necesitamos evidencia recuperable y trazabilidad.
- ¿La solución está en producción? — No; hay una demo pública y un blueprint para producción.
- ¿Qué parte está desplegada en AWS? — El frontend está en S3; el backend tiene plantillas y scripts para desplegar en ECS/RDS.
- ¿Qué significan 2/3 y 3/3? — Métricas del RAG: top-1 y top-k hit en la evaluación del corpus.

---

*Este archivo puede ajustarse según la duración acordada de la exposición o las preferencias del equipo.*
