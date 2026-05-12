# AWS Deployment Index AREP

Indice de referencia para la proyeccion cloud de AREP sobre AWS.

## Estado real del proyecto

- El frontend publico ya esta disponible en S3 como hosting estatico de demostracion.
- El backend y la base de datos cuentan con blueprint e infraestructura de referencia, no con despliegue productivo activo desde este repositorio.
- La carpeta `infra/aws/` contiene la base tecnica para continuar la publicacion en AWS.

## Artefactos principales

- [infra/aws/README.md](../../infra/aws/README.md)
- [infra/aws/main.tf](../../infra/aws/main.tf)
- [infra/aws/variables.tf](../../infra/aws/variables.tf)
- [infra/aws/outputs.tf](../../infra/aws/outputs.tf)
- [AWS Deployment Quick Guide](AWS_DEPLOYMENT_QUICK.md)
- [AWS Commands Cheatsheet](AWS_COMMANDS_CHEATSHEET.md)

## Ruta recomendada

1. Revisar el blueprint en `infra/aws/README.md`.
2. Ajustar variables y secretos.
3. Ejecutar `terraform init`, `terraform plan` y `terraform apply`.
4. Validar conectividad y health checks.
5. Repetir el flujo local con Docker Compose para comparar comportamiento.

## Alcance

- Frontend: hosting estatico + CDN.
- Backend: contenedor web.
- Datos: PostgreSQL administrado.
- Seguridad: hardening adicional pendiente para produccion.