# 🎯 AWS DEPLOYMENT - COMMAND CHEATSHEET

**Copia-pega los comandos que necesites**

---

## 📌 PRE-REQUISITOS

```bash
# Verificar que tienes todo instalado
aws --version          # AWS CLI v2
terraform --version    # Terraform >= 1.6
docker --version       # Docker
git --version          # Git
```

---

## 🔐 AWS CREDENTIALS SETUP

```bash
# Opción 1: Configurar profile
aws configure --profile arep

# Opción 2: Variables de entorno (Windows PowerShell)
$env:AWS_ACCESS_KEY_ID="AKIA..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_DEFAULT_REGION="us-east-1"

# Opción 3: Variables de entorno (macOS/Linux)
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# Verificar credenciales
aws sts get-caller-identity --profile arep
```

---

## 🏗️ ECR SETUP

```bash
# Obtener Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo $AWS_ACCOUNT_ID

# Crear repository
aws ecr create-repository \
  --repository-name arep-backend \
  --region us-east-1 \
  --profile arep

# Login Docker
aws ecr get-login-password --region us-east-1 --profile arep | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

---

## 🐳 DOCKER BUILD & PUSH

```bash
# Variables
ECR_REPO="$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arep-backend"

# Build
cd backend
docker build -t arep-backend:latest .

# Tag
docker tag arep-backend:latest $ECR_REPO:latest

# Push
docker push $ECR_REPO:latest

# Verificar en ECR
aws ecr list-images \
  --repository-name arep-backend \
  --region us-east-1 \
  --profile arep
```

---

## 🗂️ TERRAFORM SETUP

```bash
cd infra/aws

# Obtener IP
MY_IP=$(curl -s https://api.ipify.org)
echo $MY_IP

# Crear terraform.tfvars
cat > terraform.tfvars << EOF
project_name                = "arep"
environment                 = "production"
aws_region                  = "us-east-1"
backend_ingress_cidrs       = ["$MY_IP/32"]
backend_container_image     = "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest"
EOF

# Initialize
terraform init

# Validate
terraform validate

# Plan
terraform plan -out=arep.tfplan

# Apply
terraform apply arep.tfplan

# Destroy (si quieres eliminar TODO)
terraform destroy
```

---

## 📊 TERRAFORM OUTPUTS

```bash
# Ver todos los outputs
terraform output

# Ver output específico
terraform output backend_load_balancer_dns
terraform output database_endpoint
terraform output ecs_cluster_name

# Guardar en archivo
terraform output -json > deployment_info.txt
```

---

## 🚀 ECS OPERATIONS

```bash
# Variables
CLUSTER="arep-production-cluster"
SERVICE="arep-production-backend-service"
PROFILE="--profile arep"

# Obtener info del servicio
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --region us-east-1 $PROFILE

# Forzar nuevo deployment
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --force-new-deployment \
  --region us-east-1 $PROFILE

# Listar tasks
aws ecs list-tasks \
  --cluster $CLUSTER \
  --region us-east-1 $PROFILE

# Ver logs
aws logs tail /ecs/arep-production-backend --follow \
  --region us-east-1 $PROFILE
```

---

## ✅ VALIDACIÓN DE ENDPOINTS

```bash
# Variables (reemplaza con tu ALB DNS)
ALB="arep-alb-xxxxx.us-east-1.elb.amazonaws.com"

# Health check
curl http://$ALB/health

# Ready check
curl http://$ALB/ready

# RAG status
curl http://$ALB/rag/status

# Login de prueba
curl -X POST http://$ALB/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ana.patient",
    "password": "demo123"
  }'

# Crear consulta (necesita TOKEN del login)
TOKEN="<tu-token-aquí>"
curl -X POST http://$ALB/consultations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "patient_name": "Test",
    "chief_complaint": "Chest pain",
    "symptoms": ["Chest discomfort", "Shortness of breath"]
  }'

# Obtener recomendación
CONSULT_ID="<consultation-id>"
curl http://$ALB/consultations/$CONSULT_ID/recommendation \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🗄️ RDS DATABASE

```bash
# Variables
DB_ENDPOINT=$(terraform output -raw database_endpoint)
echo $DB_ENDPOINT

# Conectar a PostgreSQL
psql -h $DB_ENDPOINT \
  -U arep_admin \
  -d arep_db

# Comandos útiles en psql:
# \dt              - listar tablas
# \d tablename     - ver estructura
# SELECT * FROM consultations;  - ver datos
# \q               - salir

# Verificar conexión desde CLI
aws rds describe-db-instances \
  --db-instance-identifier arep-production-db \
  --query 'DBInstances[0].DBInstanceStatus' \
  --profile arep
```

---

## 📊 MONITOREO Y LOGS

```bash
# Ver logs en tiempo real
aws logs tail /ecs/arep-production-backend --follow \
  --region us-east-1 --profile arep

# Ver solo errores
aws logs filter-log-events \
  --log-group-name /ecs/arep-production-backend \
  --filter-pattern "ERROR" \
  --region us-east-1 --profile arep

# Ver últimas N líneas
aws logs tail /ecs/arep-production-backend --since 1h \
  --region us-east-1 --profile arep

# CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=arep-production-backend-service \
  --start-time 2026-05-10T00:00:00Z \
  --end-time 2026-05-11T00:00:00Z \
  --period 3600 \
  --statistics Average \
  --region us-east-1 --profile arep
```

---

## 💰 COSTOS

```bash
# Ver costos del mes actual
aws ce describe-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-05-31 \
  --granularity DAILY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1 --profile arep

# Usar calculator en línea
# https://calculator.aws/#/
```

---

## 🌐 FRONTEND S3

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Obtener bucket
BUCKET=$(cd infra/aws && terraform output -raw frontend_bucket_name)
echo $BUCKET

# Sincronizar archivos
aws s3 sync frontend/dist/ s3://$BUCKET \
  --delete \
  --region us-east-1 \
  --profile arep

# Ver archivos en bucket
aws s3 ls s3://$BUCKET --recursive \
  --region us-east-1 --profile arep

# URL del frontend (debe estar configurado como website)
echo "http://$BUCKET.s3-website-us-east-1.amazonaws.com"
```

---

## 🔒 SECRETS MANAGER

```bash
# Crear secret
aws secretsmanager create-secret \
  --name arep/jwt-secret \
  --secret-string "$(openssl rand -base64 32)" \
  --region us-east-1 --profile arep

# Obtener secret
aws secretsmanager get-secret-value \
  --secret-id arep/jwt-secret \
  --region us-east-1 --profile arep

# Listar secretos
aws secretsmanager list-secrets \
  --region us-east-1 --profile arep

# Eliminar secret
aws secretsmanager delete-secret \
  --secret-id arep/jwt-secret \
  --region us-east-1 --profile arep
```

---

## 🧹 CLEANUP

```bash
# Destruir toda la infraestructura
cd infra/aws
terraform destroy --profile arep

# Eliminar ECR repository
aws ecr delete-repository \
  --repository-name arep-backend \
  --force \
  --region us-east-1 --profile arep

# Eliminar secrets
aws secretsmanager delete-secret \
  --secret-id arep/jwt-secret \
  --force-delete-without-recovery \
  --region us-east-1 --profile arep

# Eliminar S3 bucket (con contenido)
aws s3 rb s3://arep-frontend-bucket --force \
  --region us-east-1 --profile arep
```

---

## 🐛 TROUBLESHOOTING

```bash
# Ver qué está pasando con ECS
aws ecs describe-services \
  --cluster arep-production-cluster \
  --services arep-production-backend-service \
  --region us-east-1 --profile arep | jq '.services[0].events | .[0:5]'

# Ver task definition
aws ecs describe-task-definition \
  --task-definition arep-production-backend \
  --region us-east-1 --profile arep

# Ver estado del Load Balancer
aws elbv2 describe-load-balancers \
  --region us-east-1 --profile arep

# Ver target health
ALB_ARN=$(aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --region us-east-1 --profile arep --output text)

TG_ARN=$(aws elbv2 describe-target-groups \
  --load-balancer-arn $ALB_ARN \
  --query 'TargetGroups[0].TargetGroupArn' \
  --region us-east-1 --profile arep --output text)

aws elbv2 describe-target-health \
  --target-group-arn $TG_ARN \
  --region us-east-1 --profile arep
```

---

## 💡 ÚTILES ONE-LINERS

```bash
# Deploy completo en una línea
cd infra/aws && terraform init && terraform plan -out=p && terraform apply p

# Obtener todas las URLs importantes
echo "Backend: http://$(terraform output -raw backend_load_balancer_dns)" && \
echo "Database: $(terraform output -raw database_endpoint):5432" && \
echo "Frontend: http://$(terraform output -raw frontend_bucket_name).s3-website-us-east-1.amazonaws.com"

# Ver estado de todos los recursos
terraform show -no-color | grep "resource"

# Validar token JWT
TOKEN="<tu-token>" && \
echo $TOKEN | cut -d'.' -f2 | base64 -d | jq '.'

# Monitoreo en tiempo real (cada 5 seg)
watch -n 5 'aws ecs describe-services --cluster arep-production-cluster --services arep-production-backend-service --query "services[0].[serviceName,desiredCount,runningCount]" --profile arep'
```

---

## 📖 REFERENCIAS

- AWS CLI: https://docs.aws.amazon.com/cli/
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- ECS: https://docs.aws.amazon.com/ecs/
- RDS: https://docs.aws.amazon.com/rds/
- ECR: https://docs.aws.amazon.com/ecr/

---

**Guardá esta página como favorito** ⭐

**Última actualización**: Mayo 10, 2026
