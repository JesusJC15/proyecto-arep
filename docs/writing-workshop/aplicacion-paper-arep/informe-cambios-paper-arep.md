# Informe de Cambios Aplicados al Paper AREP

## Datos generales

- Titulo del manuscrito: Arquitectura de una Plataforma Inteligente de Triaje Medico Modular Basada en IA, RAG y Arquitecturas Cloud
- Autor o equipo: Natalia Espitia Espinel, Jesus Alberto Jauregui Conde, Mayerlly Suarez Correa
- Fecha de intervencion: 2026-05-06
- Documento intervenido: `paper/main.tex`
- Version inicial revisada: manuscrito original de segunda entrega
- Version final generada: manuscrito fortalecido tras aplicacion del taller

## Registro de cambios

| ID | Problema detectado | Seccion afectada | Evidencia del texto original | Tipo de problema | Cambio realizado | Justificacion del cambio | Impacto esperado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | El vacio de conocimiento no estaba formulado con suficiente precision. | Introduccion / Estado del arte | El texto hablaba de relevancia de RAG y salud digital, pero no explicitaba con fuerza que faltaba una arquitectura defendible que uniera triaje, evidencia y escalamiento. | coherencia | Se reescribio la subseccion de continuidad para formular un vacio practico explicito y conectar mejor antecedentes con propuesta. | Mejora la justificacion del articulo y fortalece la motivacion del lector. | Mayor claridad sobre por que el trabajo existe y que aporta. |
| 2 | La introduccion mencionaba la propuesta, pero no cerraba con contribuciones claramente delimitadas. | Introduccion | Las contribuciones aparecian distribuidas en varios parrafos. | estructura | Se agrego un cierre de introduccion con contribucion principal doble: arquitectura defendible y prototipo observable. | Ayuda a que la promesa del trabajo quede visible desde el inicio. | Mayor legibilidad academica y mejor alineacion con conclusiones. |
| 3 | El paper no mostraba evidencia concreta del repositorio dentro de la seccion del MVP. | Arquitectura del prototipo MVP | La implementacion se describia de forma general, sin detallar rutas, servicios o componentes visibles. | soporte | Se agrego una subseccion de implementacion observable en el repositorio con backend, RAG y frontends. | Vincula la arquitectura con artefactos reales y reduce la percepcion de conceptualidad. | Mayor credibilidad tecnica del manuscrito. |
| 4 | No existia una seccion de resultados. | Resultados | El manuscrito pasaba de flujo principal a riesgos y siguiente fase. | resultados | Se incorporo una seccion completa de resultados y validacion inicial. | Era la principal carencia del manuscrito segun la rubrica del taller. | Incremento de completitud academica y mejor defensa externa. |
| 5 | No habia evaluacion de atributos de calidad del prototipo. | Resultados | El paper mencionaba trazabilidad como atributo dominante, pero no la evaluaba explicitamente. | resultados | Se agrego una tabla cualitativa con trazabilidad, seguridad basica, modularidad, usabilidad operativa y escalabilidad tecnica. | Permite sostener el discurso arquitectonico con evidencia minima observable. | Mayor coherencia entre objetivos, arquitectura y validacion. |
| 6 | Las vistas arquitectonicas existian fuera del articulo, pero no habia figuras integradas ni explicadas. | Arquitectura general / MVP | Solo se incluia una tabla de vistas entregadas. | figuras | Se agregaron dos figuras esquematicas en LaTeX y referencias directas a ellas en el cuerpo del texto. | Responde a una debilidad frecuente del manuscrito y fortalece el criterio visual de la rubrica. | Mejor comprension del flujo y de la relacion entre arquitectura objetivo y MVP. |
| 7 | Algunas secciones se acercaban a enumeraciones tecnicas sin interpretacion suficiente. | Arquitectura general / Modelo / Flujo | Varias listas de componentes y entidades no siempre se conectaban con una lectura argumentativa. | redaccion | Se convirtieron varios listados en parrafos interpretativos y se reforzaron transiciones. | El taller busca evitar manuscritos tipo glosario. | Mayor continuidad argumentativa del documento. |
| 8 | Las conclusiones no aprovechaban evidencia de resultados porque esa seccion no existia. | Conclusiones | El cierre era correcto, pero descansaba casi por completo en la arquitectura y el trabajo futuro. | coherencia | Se reescribieron las conclusiones para enlazarlas con la validacion funcional inicial y las limitaciones reales. | Cierra mejor el arco argumentativo del manuscrito. | Final mas solido y mejor preparado para evaluacion externa. |

## Resumen ejecutivo de mejoras

### Cambios de mayor impacto

- incorporacion de una seccion de resultados y validacion inicial;
- integracion del repositorio como evidencia del prototipo;
- insercion de figuras esquematicas referenciadas en el texto.

### Riesgos que fueron corregidos

- que el manuscrito pareciera puramente conceptual;
- que la propuesta arquitectonica no estuviera acompanada por evidencia funcional;
- que el lector no contara con apoyo visual dentro del paper.

### Aspectos pendientes para una siguiente iteracion

- compilar el PDF final y revisar ajuste visual de tablas y figuras;
- fortalecer la bibliografia con fuentes mas robustas o mas directamente comparables;
- incorporar mediciones cuantitativas reales en la tercera entrega.
