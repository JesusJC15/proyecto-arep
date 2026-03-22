# ADR-003 - Autenticacion basica con JWT y roles simples

- Estado: Aceptada
- Fecha: 2026-03-22

## Contexto

El prototipo necesita separar responsabilidades entre paciente y profesional sin incorporar, por ahora, un proveedor de identidad externo.

## Decision

Se adopta autenticacion basada en JWT con dos roles: `patient` y `professional`.

## Justificacion

- Es suficiente para demostrar separacion de acceso en el MVP.
- Evita acoplar la segunda entrega a servicios gestionados como Cognito.
- Mantiene una ruta clara de evolucion hacia seguridad mas robusta en la tercera entrega.

## Consecuencias

- La seguridad es basica y no debe presentarse como lista para produccion.
- El backend debe encapsular la validacion del token para poder migrar a un proveedor externo despues.
