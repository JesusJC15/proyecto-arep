# Demo Script AREP

Guion de demostracion para presentar el flujo completo del prototipo.

## Apertura

"AREP es una plataforma academica de triaje medico asistido por IA. La demo muestra como un paciente registra sintomas, el sistema genera una recomendacion con evidencia recuperada y un profesional puede revisar el caso escalado."

## Paso 1. Mostrar la base del sistema

1. Abrir http://localhost:4173.
2. Explicar que el frontend consume la API real.
3. Mostrar que la evidencia RAG y la trazabilidad aparecen en la interfaz.

## Paso 2. Flujo del paciente

1. Iniciar sesion como `ana.patient`.
2. Crear una consulta con sintomas simples o moderados.
3. Ejecutar el triage.
4. Mostrar severidad, decision, score y evidencia recuperada.
5. Abrir la fuente de un documento si se quiere evidenciar trazabilidad.

Mensaje sugerido:

"El sistema no solo clasifica; tambien explica por que recupero esta evidencia y como se relaciona con la recomendacion."

## Paso 3. Mostrar estado del RAG

1. Abrir http://localhost:8000/rag/status.
2. Señalar corpus version, indice y modelo de embedding.
3. Mencionar que el indice es reproducible y versionado.

## Paso 4. Flujo profesional

1. Cerrar sesion o abrir otra ventana.
2. Iniciar sesion como `dr.suarez`.
3. Abrir la bandeja profesional.
4. Tomar el caso.
5. Marcarlo como revisado.

Mensaje sugerido:

"El profesional recibe casos ya estructurados, con la recomendacion y la evidencia suficiente para revisar sin perder trazabilidad."

## Cierre

"La contribucion principal es integrar triaje, evidencia RAG y escalamiento profesional en una arquitectura reproducible y defendible."

## Plan B si algo falla

1. Verificar `docker compose ps`.
2. Verificar `http://localhost:8000/health`.
3. Verificar `http://localhost:8000/ready`.
4. Reiniciar con `docker compose down` y `docker compose up --build -d`.