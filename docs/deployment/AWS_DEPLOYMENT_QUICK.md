# AWS Deployment Quick Guide AREP

Guia rapida para proyectar la demo de AREP hacia AWS.

## Antes de empezar

- Confirmar que el frontend publico ya existe en S3 como demo.
- Confirmar que el backend y la base de datos siguen siendo blueprint, no produccion.
- Revisar [AWS Deployment Index](AWS_DEPLOYMENT_INDEX.md).

## Paso 1. Revisar el blueprint

Abrir `infra/aws/README.md` y revisar:

- topologia propuesta,
- variables de entrada,
- limites del alcance,
- artefactos Terraform disponibles.

## Paso 2. Ajustar configuracion

Definir valores para:

- region,
- nombres de recursos,
- URL del backend,
- secret de JWT,
- origenes CORS,
- datos de base de datos.

## Paso 3. Ejecutar Terraform

```bash
terraform -chdir=infra/aws init
terraform -chdir=infra/aws plan
terraform -chdir=infra/aws apply
```

## Paso 4. Validar

- Confirmar que el frontend sigue respondiendo.
- Confirmar que el backend responde `health` y `ready`.
- Confirmar que la configuracion del RAG sigue coherente con `artifacts/rag-index.json`.

## Paso 5. Documentar

- Guardar outputs relevantes.
- Registrar decisiones de seguridad y red.
- Mantener la documentacion sincronizada con el estado real del despliegue.

## Nota

Este guia describe una trayectoria de despliegue, no una publicacion productiva ya resuelta.