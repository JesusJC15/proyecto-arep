# AWS Commands Cheatsheet AREP

Comandos de referencia para trabajar con el blueprint de AWS.

## Terraform

```bash
terraform -chdir=infra/aws init
terraform -chdir=infra/aws fmt -recursive
terraform -chdir=infra/aws validate
terraform -chdir=infra/aws plan
terraform -chdir=infra/aws apply
terraform -chdir=infra/aws output
terraform -chdir=infra/aws destroy
```

## Validacion local antes de publicar

```bash
docker compose config
docker compose up --build -d
curl http://localhost:8000/health
curl http://localhost:8000/rag/status
```

## Variables utiles

- `AREP_DATABASE_URL`
- `AREP_JWT_SECRET`
- `AREP_CORS_ORIGINS`
- `AREP_RAG_INDEX_ARTIFACT_PATH`

## Recomendacion operativa

- Revisar primero el blueprint.
- Aplicar cambios con Terraform.
- Confirmar health checks antes de considerar el despliegue listo.