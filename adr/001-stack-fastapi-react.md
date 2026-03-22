# ADR-001 - FastAPI para backend y React para frontends

- Estado: Aceptada
- Fecha: 2026-03-22

## Contexto

La segunda entrega necesita un backend con contratos claros, facil validacion de datos y bajo costo de integracion con componentes de IA. Tambien requiere dos experiencias de usuario separadas: paciente y profesional.

## Decision

Se adopta `FastAPI` para el backend del MVP y `React` para los dos frontends web.

## Justificacion

- FastAPI acelera el prototipado del API y el modelado de contratos con Pydantic.
- React permite separar facilmente las experiencias por rol sin introducir una arquitectura frontend excesivamente pesada.
- La combinacion reduce friccion tecnica para una tercera entrega enfocada en implementacion y evaluacion.

## Consecuencias

- El proyecto se aleja del stack Java clasico del curso, por lo que la defensa debe enfatizar la cercania de FastAPI con el dominio IA/RAG.
- Se requiere definir desde el inicio contratos estables entre frontend y backend para evitar crecimiento desordenado.
