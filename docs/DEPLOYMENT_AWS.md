# AWS DEPLOYMENT GUIDE - AREP Triage Platform

**Guía paso a paso para desplegar AREP en AWS**

---

## 📋 Prerequisitos

### Antes de Empezar

**Verificar que tienes:**
- [ ] Cuenta AWS activa
- [ ] Permiso para crear recursos (EC2, RDS, ECS, ECR, S3, IAM)
- [ ] $50-200 USD presupuestados (estimado mensual)
- [ ] 2-3 horas disponibles

### Software Requerido (Local)

Instalar en tu máquina:

```bash
# 1. AWS CLI v2
# Windows: https://awscli.amazonaws.com/AWSCLIV2.msi
# macOS: brew install awscli
# Linux: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

aws --version
# Expected: aws-cli/2.x.x

# 2. Terraform >= 1.6.0
# https://www.terraform.io/downloads
terraform --version
# Expected: v1.x.x

# 3. Docker (para construir imágenes)
# Ya deberías tenerlo del setup local
docker --version

# 4. Git (para clonar repo)
git --version
```

---

## 🔐 Step 1: Configurar AWS Credentials

### Opción A: AWS CLI Profile (Recomendado)

```bash
# 1. Ir a AWS Console → IAM → Users
# 2. Crear nuevo usuario "arep-deployer" con acceso programático
# 3. Asignar políticas:
#    - AmazonEC2FullAccess
#    - AmazonRDSFullAccess
#    - AmazonECS_FullAccess
#    - AmazonElasticContainerRegistryPowerUser
#    - AmazonS3FullAccess
#    - CloudWatchLogsFullAccess
#    - IAMFullAccess

# 4. Descargar credentials CSV

# 5. Configurar profile en tu máquina
aws configure --profile arep

# Te pedirá:
# AWS Access Key ID: [pega el valor del CSV]
# AWS Secret Access Key: [pega el valor del CSV]
# Default region name: us-east-1
# Default output format: json

# 6. Verificar credenciales
aws sts get-caller-identity --profile arep

# Expected output:
# {
#   "UserId": "AIDAI...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/arep-deployer"
# }
```

### Opción B: Variables de Entorno

```bash
# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="AKIA..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_DEFAULT_REGION="us-east-1"

# macOS/Linux
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# Verificar
aws sts get-caller-identity
```

---

## 🏗️ Step 2: Preparar Infraestructura en AWS

### 2.1 Crear ECR Repository (para imágenes Docker)

```bash
# Login en AWS Console → ECR o usa CLI:

aws ecr create-repository \
  --repository-name arep-backend \
  --region us-east-1 \
  --profile arep

# Respuesta esperada:
# {
#   "repository": {
#     "repositoryArn": "arn:aws:ecr:us-east-1:123456789012:repository/arep-backend",
#     "registryId": "123456789012",
#     "repositoryName": "arep-backend",
#     "repositoryUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-backend"
#   }
# }

# Guarda el repositoryUri (lo necesitarás después)
ECR_REPO="123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-backend"
```

### 2.2 Crear Secreto en AWS Secrets Manager

```bash
# Crear secreto para JWT_SECRET

aws secretsmanager create-secret \
  --name arep/jwt-secret \
  --secret-string "$(openssl rand -base64 32)" \
  --region us-east-1 \
  --profile arep

# Para base de datos, también crear:

aws secretsmanager create-secret \
  --name arep/db-password \
  --secret-string "$(openssl rand -base64 16)" \
  --region us-east-1 \
  --profile arep
```

---

## 🐳 Step 3: Construir y Publicar Imagen Docker

### 3.1 Login en ECR

```bash
# Get login token y login en ECR
aws ecr get-login-password --region us-east-1 --profile arep | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# Expected: Login Succeeded
```

### 3.2 Construir imagen backend

```bash
cd backend

# Build image
docker build -t arep-backend:latest .

# Tag con ECR URI
docker tag arep-backend:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest

# Push a ECR
docker push \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest

# Expected: Successfully pushed

# Verificar en AWS Console → ECR → Repositories → arep-backend
```

### 3.3 Construir imagen frontend (opcional, si usas ECS)

```bash
cd ../frontend

# Build
docker build -t arep-frontend:latest .

# Tag
docker tag arep-frontend:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-frontend:latest

# Push
docker push \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-frontend:latest
```

---

## 🗂️ Step 4: Preparar Terraform

### 4.1 Actualizar variables

```bash
cd infra/aws

# Abrir terraform.tfvars
cat > terraform.tfvars << 'EOF'
project_name = "arep"
environment  = "production"
aws_region   = "us-east-1"

# Networking
vpc_cidr                = "10.42.0.0/16"
public_subnet_cidr      = "10.42.1.0/24"
private_subnet_a_cidr   = "10.42.10.0/24"
private_subnet_b_cidr   = "10.42.11.0/24"
public_subnet_az        = "us-east-1a"
private_subnet_a_az     = "us-east-1a"
private_subnet_b_az     = "us-east-1b"

# Backend access (tu IP)
backend_ingress_cidrs = ["YOUR_IP/32"]  # Reemplaza YOUR_IP

# Database
db_instance_class   = "db.t3.micro"  # Cambiar a db.t3.small si necesitas más
db_allocated_storage = 20
db_storage_type     = "gp3"

# Backend image en ECR
backend_container_image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest"
EOF
```

### 4.2 Inicializar Terraform

```bash
# Inicializar (descarga providers)
terraform init

# Output esperado:
# Terraform has been successfully configured!
```

### 4.3 Validar configuración

```bash
# Validar sintaxis
terraform validate

# Output esperado:
# Success! The configuration is valid.

# Revisar plan (SIN hacer cambios aún)
terraform plan -out=arep.tfplan

# Esto mostrará todos los recursos que se van a crear
# Verifica que tiene sentido:
# - 1 VPC
# - 3 subnets
# - Security groups
# - RDS instance
# - ECS cluster, service, task definition
# - S3 bucket para frontend
# - Load balancer
```

---

## ⚙️ Step 5: Desplegar Infraestructura

### 5.1 Aplicar Terraform

```bash
# Aplicar cambios
terraform apply arep.tfplan

# Esto tomará 10-15 minutos

# Output esperado:
# aws_vpc.main: Creating...
# aws_security_group.backend: Creating...
# aws_db_instance.postgres: Creating...
# ...
# Apply complete! Resources: 15 added

# Guardar outputs
terraform output > deployment_info.txt
cat deployment_info.txt
```

### 5.2 Obtener información de deployment

```bash
# Ver endpoints importantes
terraform output -json

# Esto mostrará:
# {
#   "database_endpoint": "arep-production-db.xxxxx.us-east-1.rds.amazonaws.com",
#   "backend_load_balancer_dns": "arep-alb-xxx.us-east-1.elb.amazonaws.com",
#   "ecs_cluster_name": "arep-production-cluster",
#   "backend_service_name": "arep-production-backend-service"
# }

# Guarda estos valores para referencia
```

---

## 🔗 Step 6: Configurar Base de Datos

### 6.1 Esperar que RDS esté listo

```bash
# Verificar estado de RDS (debería estar "available")
aws rds describe-db-instances \
  --db-instance-identifier arep-production-db \
  --region us-east-1 \
  --profile arep \
  --query 'DBInstances[0].DBInstanceStatus'

# Output: available (esperar a que diga esto)
```

### 6.2 Obtener endpoint de base de datos

```bash
DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier arep-production-db \
  --region us-east-1 \
  --profile arep \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo $DB_ENDPOINT
# Output: arep-production-db.xxxxx.us-east-1.rds.amazonaws.com
```

### 6.3 Conectar a la base de datos

```bash
# Necesitarás psql instalado:
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql-client
# Windows: Descargar de https://www.postgresql.org/download/windows/

# Conectar (la contraseña viene de variables.tf)
psql -h $DB_ENDPOINT \
  -U arep_admin \
  -d arep_db \
  -c "SELECT version();"

# Si funciona, verás la versión de PostgreSQL
```

### 6.4 Ejecutar migraciones de schema

```bash
# Las migraciones se correrán automáticamente cuando ECS lance el backend
# Pero puedes verificar que la BD está vacía:

psql -h $DB_ENDPOINT \
  -U arep_admin \
  -d arep_db \
  -c "\dt"

# Output: Did not find any relation named "..." (normal, está vacía)
```

---

## 🚀 Step 7: Desplegar Backend en ECS

### 7.1 Actualizar ECS Task Definition

```bash
# El Terraform ya creó la task definition
# Pero necesita que verifiques los secretos

# Ir a AWS Console → Secrets Manager
# Verificar que existen:
# - arep/jwt-secret
# - arep/db-password

# Si no existen, crearlas:
aws secretsmanager create-secret \
  --name arep/jwt-secret \
  --secret-string "your-super-secret-key-change-in-prod" \
  --region us-east-1 \
  --profile arep

aws secretsmanager create-secret \
  --name arep/db-password \
  --secret-string "your-secure-password" \
  --region us-east-1 \
  --profile arep
```

### 7.2 Forzar actualización de servicio

```bash
# Esto hará que ECS lance la imagen nueva
aws ecs update-service \
  --cluster arep-production-cluster \
  --service arep-production-backend-service \
  --force-new-deployment \
  --region us-east-1 \
  --profile arep

# Output:
# {
#   "service": {
#     "serviceName": "arep-production-backend-service",
#     "taskDefinition": "arn:aws:ecs:...",
#     "status": "ACTIVE"
#   }
# }
```

### 7.3 Monitorear deployment

```bash
# Ver tareas en ejecución
aws ecs describe-services \
  --cluster arep-production-cluster \
  --services arep-production-backend-service \
  --region us-east-1 \
  --profile arep

# Ver logs del contenedor
aws logs tail /ecs/arep-production-backend --follow \
  --region us-east-1 \
  --profile arep

# Esperar a que veas:
# "Uvicorn running on http://0.0.0.0:8000"
# "Database migration completed"
```

---

## ✅ Step 8: Validar Deployment

### 8.1 Obtener Load Balancer DNS

```bash
ALB_DNS=$(terraform output -raw backend_load_balancer_dns)
echo $ALB_DNS
# Output: arep-alb-xxxxx.us-east-1.elb.amazonaws.com
```

### 8.2 Probar endpoints

```bash
# Health check
curl http://$ALB_DNS/health
# Expected: {"status":"ok"}

# Readiness
curl http://$ALB_DNS/ready
# Expected: {"status":"ready"}

# RAG status
curl http://$ALB_DNS/rag/status
# Expected: {"corpus_version":"...", "status":"ready"}
```

### 8.3 Probar autenticación

```bash
curl -X POST http://$ALB_DNS/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ana.patient",
    "password": "demo123"
  }'

# Expected:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "user": {"id": "...", "username": "ana.patient", "role": "patient"}
# }
```

### 8.4 Probar flujo completo

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://$ALB_DNS/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ana.patient","password":"demo123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 2. Crear consulta
CONSULT=$(curl -s -X POST http://$ALB_DNS/consultations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "patient_name":"Ana Test",
    "chief_complaint":"Chest pain",
    "symptoms":["Chest discomfort","Shortness of breath"]
  }' | grep -o '"id":"[^"]*' | cut -d'"' -f4)

echo "Consultation ID: $CONSULT"

# 3. Ejecutar triage
curl -X POST http://$ALB_DNS/consultations/$CONSULT/triage \
  -H "Authorization: Bearer $TOKEN"

# Expected: Recomendación con evidencias
```

---

## 🌐 Step 9: Desplegar Frontend (Opcional)

### 9.1 Build frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Build para producción
npm run build

# Output: dist/ directory creado
```

### 9.2 Publicar a S3

```bash
# Obtener bucket name
BUCKET_NAME=$(terraform output -raw frontend_bucket_name)
echo $BUCKET_NAME

# Sincronizar archivos
aws s3 sync dist/ s3://$BUCKET_NAME \
  --region us-east-1 \
  --profile arep \
  --delete

# Esperar confirmación
```

### 9.3 Obtener frontend URL

```bash
# El S3 debe estar configurado como website
FRONTEND_URL=$(aws s3 website s3://$BUCKET_NAME \
  --region us-east-1 \
  --profile arep \
  --query 'Website' \
  --output text)

echo "Frontend disponible en: $FRONTEND_URL"
```

---

## 📊 Step 10: Monitoreo y Costos

### 10.1 CloudWatch Dashboard

```bash
# El Terraform debería haber creado dashboards
# Ir a AWS Console → CloudWatch → Dashboards
# Buscar "arep-production"

# Verificar:
# - ECS task CPU/Memory
# - RDS CPU/Storage
# - ALB request count
# - Error rates
```

### 10.2 Configurar alarmas

```bash
# Alarma si alta CPU
aws cloudwatch put-metric-alarm \
  --alarm-name arep-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --region us-east-1 \
  --profile arep

# Alarma si alta memoria
aws cloudwatch put-metric-alarm \
  --alarm-name arep-high-memory \
  --alarm-description "Alert when Memory > 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --region us-east-1 \
  --profile arep
```

### 10.3 Estimador de costos

```bash
# Costos mensuales estimados:
# - RDS db.t3.micro: $15-20/mes
# - ECS Fargate (0.5 CPU, 1GB RAM): $20-30/mes
# - ALB: $16/mes
# - NAT Gateway: $30/mes
# - S3: $1-5/mes
# - Data transfer: $5-10/mes
# ─────────────────────────────
# TOTAL: ~$90-110/mes

# Para verificar costos reales:
aws ce describe-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-05-10 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --region us-east-1 \
  --profile arep
```

---

## 🛑 Step 11: Destruir Infraestructura (Opcional)

```bash
# Si necesitas eliminar TODO (para ahorrar costos):

cd infra/aws

# Ver qué se va a eliminar
terraform plan -destroy

# Eliminar
terraform destroy

# Confirmar escribiendo "yes"

# Verificar en AWS Console que todos los recursos desaparecieron
```

---

## 🚨 Troubleshooting

### ECS Task no inicia

```bash
# Ver logs
aws logs tail /ecs/arep-production-backend --follow

# Ver task events
aws ecs describe-tasks \
  --cluster arep-production-cluster \
  --tasks $(aws ecs list-tasks \
    --cluster arep-production-cluster \
    --query 'taskArns[0]' \
    --output text) \
  --region us-east-1 \
  --profile arep
```

### Conexión a RDS falla

```bash
# Verificar security group
aws ec2 describe-security-groups \
  --filter Name=group-name,Values="*db*" \
  --region us-east-1 \
  --profile arep

# Verificar que backend security group puede llegar a DB
# (Regla de ingreso en DB security group debería permitir puerto 5432 del backend)
```

### Load Balancer no responde

```bash
# Ver health de targets
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --load-balancer-arn $(aws elbv2 describe-load-balancers \
      --query 'LoadBalancers[0].LoadBalancerArn' \
      --region us-east-1 \
      --profile arep \
      --output text) \
    --query 'TargetGroups[0].TargetGroupArn' \
    --region us-east-1 \
    --profile arep \
    --output text) \
  --region us-east-1 \
  --profile arep
```

---

## 📝 Resumen

### Lo que se desplegó:

✅ VPC con 3 subnets (1 pública, 2 privadas)  
✅ RDS PostgreSQL (db.t3.micro)  
✅ ECS Fargate cluster con backend  
✅ Application Load Balancer  
✅ NAT Gateway para conectividad  
✅ S3 bucket para frontend  
✅ CloudWatch logs y monitoring  
✅ Secrets Manager para credenciales  

### URLs importantes:

- **Backend API**: `http://<ALB_DNS>/api`
- **Frontend**: `http://<S3_BUCKET>.s3-website-us-east-1.amazonaws.com`
- **CloudWatch Logs**: AWS Console → CloudWatch → Log Groups
- **RDS Endpoint**: Ver en terraform outputs

### Siguiente: Actualizar DNS

```bash
# Si tienes dominio propio:
# 1. Crear CNAME record apuntando a ALB DNS
# 2. Configurar SSL con ACM (AWS Certificate Manager)
# 3. Actualizar Load Balancer para HTTPS
```

---

**Last Updated**: May 10, 2026  
**Version**: 1.0  
**Estimated Deploy Time**: 30-45 minutes  
**Estimated Monthly Cost**: $90-110 USD
