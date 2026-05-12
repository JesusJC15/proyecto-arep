# Blueprint AWS base - AREP

Este directorio contiene un blueprint base para proyectar AREP sobre AWS. Contiene plantillas y recomendaciones para desplegar frontend estático, backend contenedorizado y la base de datos.

## Objetivo

Mapear la topologia local de `frontend + backend + postgres` hacia una arquitectura AWS defendible:

- frontend local -> hosting estatico + CDN
- backend contenedorizado -> servicio en ECS Fargate
- postgres local -> Amazon RDS PostgreSQL

## Cobertura del blueprint

- red base:
  - VPC
  - subredes publicas y privadas
  - security groups
- aplicacion:
  - bucket para frontend
  - ECR para imagen backend
  - ECS cluster
  - task definition y service
- datos:
  - DB subnet group
  - RDS PostgreSQL

## Artefactos

- [main.tf](main.tf)
- [variables.tf](variables.tf)
- [outputs.tf](outputs.tf)

## Limites

- el frontend ya puede desplegarse como hosting estático en S3 (ej. la demo pública está en S3).
- las plantillas aquí son base y requieren ajustes para producción (secrets, WAF, observabilidad, backups).
- no incluye integraciones propietarias (Bedrock) ni vector store productivo por defecto
