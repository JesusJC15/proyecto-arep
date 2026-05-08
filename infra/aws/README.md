# Blueprint AWS base - AREP

Este directorio contiene un blueprint base para proyectar AREP sobre AWS sin exigir despliegue real en esta fase.

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

- no despliega realmente en AWS en esta fase
- no incluye Bedrock ni vector store productivo
- no incorpora WAF, Secrets Manager ni observabilidad avanzada
