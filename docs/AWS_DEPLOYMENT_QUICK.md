# 🚀 AWS DEPLOYMENT - RESUMEN 5 PASOS

**Si solo tienes 1 hora, empieza aquí**

---

## 📋 RESUMEN VISUAL

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE                                              │
│  ┌──────────────────────────────┐                           │
│  │ 1. Configure AWS Credentials │                           │
│  │    aws configure --profile   │                           │
│  └──────────────────────────────┘                           │
│            ↓                                                  │
│  ┌──────────────────────────────┐                           │
│  │ 2. Build & Push Docker       │                           │
│  │    docker build + aws push   │                           │
│  └──────────────────────────────┘                           │
│            ↓                                                  │
│  ┌──────────────────────────────┐                           │
│  │ 3. Deploy Terraform          │                           │
│  │    terraform apply           │                           │
│  └──────────────────────────────┘                           │
│            ↓ (15 min de espera)                             │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  AWS CLOUD                                                  │
│  ┌──────────────────────────────┐                           │
│  │ 4. Backend corriendo en ECS  │                           │
│  │    Database listo en RDS     │                           │
│  └──────────────────────────────┘                           │
│            ↓ (5 min de espera)                              │
│  ┌──────────────────────────────┐                           │
│  │ 5. Validar endpoints         │                           │
│  │    curl http://<ALB>/health  │                           │
│  └──────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ OPCIÓN A: Script Automático (RECOMENDADO)

### Si usas macOS/Linux:

```bash
cd proyecto-arep
chmod +x scripts/deploy-to-aws.sh
bash scripts/deploy-to-aws.sh

# El script te pedirá:
# - AWS Profile
# - AWS Region
# - AWS Account ID
# - Tu IP (para acceso)

# Y hace TODO automáticamente:
# ✅ Verifica prerequisitos
# ✅ Crea ECR repository
# ✅ Crea secrets
# ✅ Build & Push Docker
# ✅ Terraform init, plan, apply
# ✅ Espera a que ECS esté listo
# ✅ Valida endpoints
```

**Tiempo**: 40-50 minutos  
**Automático**: 95%  
**Recomendado**: ✅ SÍ

---

## 📝 OPCIÓN B: Manual Step-by-Step

### PASO 1️⃣: AWS Setup (5 min)

```bash
# 1a. Ir a AWS Console y crear IAM user
# https://console.aws.amazon.com/iam/
# Nombre: arep-deployer
# Permisos: AmazonEC2FullAccess, AmazonRDSFullAccess, AmazonECS_FullAccess, etc.
# Descargar CSV con credentials

# 1b. Configurar AWS CLI
aws configure --profile arep

# Te pedirá:
# AWS Access Key ID: [del CSV]
# AWS Secret Access Key: [del CSV]
# Default region: us-east-1
# Default output format: json

# 1c. Verificar
aws sts get-caller-identity --profile arep
```

**Status**: ✅ Listo cuando ves tu Account ID

---

### PASO 2️⃣: Docker Build & Push (15 min)

```bash
# 2a. Obtener tu Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo $AWS_ACCOUNT_ID

# 2b. Crear ECR repository
aws ecr create-repository \
  --repository-name arep-backend \
  --region us-east-1 \
  --profile arep

# 2c. Login en Docker
aws ecr get-login-password --region us-east-1 --profile arep | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 2d. Build y Push
cd backend
docker build -t arep-backend:latest .
docker tag arep-backend:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest
docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest
cd ..
```

**Status**: ✅ Imagen visible en AWS Console → ECR

---

### PASO 3️⃣: Terraform Deploy (20 min + 15 min espera)

```bash
# 3a. Obtener tu IP
MY_IP=$(curl -s https://api.ipify.org)
echo $MY_IP

# 3b. Crear terraform.tfvars
cd infra/aws
cat > terraform.tfvars << EOF
project_name                = "arep"
environment                 = "production"
aws_region                  = "us-east-1"
backend_ingress_cidrs       = ["$MY_IP/32"]
backend_container_image     = "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/arep-backend:latest"
EOF

# 3c. Init + Plan
terraform init
terraform plan -out=arep.tfplan

# 3d. Apply (ESTE ES EL PUNTO DE NO RETORNO)
terraform apply arep.tfplan

# ⏰ Esperar 15 minutos...

# 3e. Obtener outputs
terraform output -json > deployment_info.txt
ALB_DNS=$(terraform output -raw backend_load_balancer_dns)
echo "Backend disponible en: http://$ALB_DNS"
cd ../..
```

**Status**: ✅ Todo los recursos en AWS, ECS task en RUNNING

---

### PASO 4️⃣: Validar (5 min)

```bash
# Reemplaza con tu ALB_DNS
ALB_DNS="arep-alb-xxxxx.us-east-1.elb.amazonaws.com"

# Test 1: Health
curl http://$ALB_DNS/health
# Respuesta: {"status":"ok"}

# Test 2: Login
curl -X POST http://$ALB_DNS/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ana.patient","password":"demo123"}'
# Respuesta: access_token, user info

# Test 3: Crear consulta
TOKEN=$(curl -s -X POST http://$ALB_DNS/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ana.patient","password":"demo123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

curl -X POST http://$ALB_DNS/consultations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "patient_name":"Test",
    "chief_complaint":"Chest pain",
    "symptoms":["Chest discomfort","Shortness of breath"]
  }'
```

**Status**: ✅ Backend responde, flujo completo funciona

---

### PASO 5️⃣: Frontend (Opcional)

```bash
# Si quieres frontend en S3
cd frontend
npm run build

BUCKET=$(terraform output -raw frontend_bucket_name)
aws s3 sync dist/ s3://$BUCKET --profile arep

# Frontend estará en:
# http://$BUCKET.s3-website-us-east-1.amazonaws.com
```

**Status**: ✅ Frontend accesible

---

## 💰 COSTOS ESTIMADOS

| Servicio | Costo/mes |
|----------|-----------|
| RDS db.t3.micro | $15 |
| ECS Fargate 0.5 CPU | $20 |
| ALB | $16 |
| NAT Gateway | $30 |
| S3 + Data Transfer | $10 |
| **TOTAL** | **~$90-110** |

**Cómo ahorrar**:
- Usar RDS Free Tier (si aplicas)
- Reducir compute de ECS
- Destruir cuando no uses: `terraform destroy`

---

## 🛠️ ARCHIVOS IMPORTANTES

| Archivo | Propósito |
|---------|----------|
| `infra/aws/main.tf` | Infraestructura (VPC, RDS, ECS, ALB) |
| `infra/aws/variables.tf` | Variables de Terraform |
| `infra/aws/terraform.tfvars` | EDITAR AQUÍ antes de deploy |
| `scripts/deploy-to-aws.sh` | Script automático |
| `docs/DEPLOYMENT_AWS.md` | Guía completa con troubleshooting |

---

## 📞 QUICK REFERENCE

### Obtener información después del deploy

```bash
cd infra/aws

# Ver todos los outputs
terraform output

# Ver ALB DNS
terraform output backend_load_balancer_dns

# Ver Database endpoint
terraform output database_endpoint

# Ver ECS cluster
terraform output ecs_cluster_name
```

### Monitorear ejecución

```bash
# Ver logs en tiempo real
aws logs tail /ecs/arep-production-backend --follow --profile arep

# Ver estado de tasks
aws ecs describe-services \
  --cluster arep-production-cluster \
  --services arep-production-backend-service \
  --profile arep

# Ver costos
aws ce describe-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-05-31 \
  --granularity DAILY \
  --metrics "BlendedCost" \
  --profile arep
```

### Destruir TODO (ahorrar dinero)

```bash
cd infra/aws
terraform destroy --profile arep

# Escribir "yes" cuando pregunte
```

---

## ✅ DECISIÓN FINAL

| Opción | Tiempo | Complejidad | Recomendación |
|--------|--------|-------------|---------------|
| **Script automático** | 40-50 min | Muy bajo | ✅ **MEJOR** |
| **Manual step-by-step** | 60-90 min | Medio | Para aprender |
| **AWS Console manual** | 120+ min | Alto | No recomendado |

---

## 🎯 PRÓXIMOS PASOS DESPUÉS DEL DEPLOY

1. ✅ Validar que todo funciona (curl tests)
2. ⚠️ Configurar DNS personalizado (si tienes dominio)
3. 🔒 Configurar HTTPS/SSL (ACM Certificate Manager)
4. 📊 Configurar CloudWatch alarmas
5. 💾 Crear plan de backup para RDS
6. 🔑 Rotar credenciales periódicamente

---

**¿Listo?**

- **Opción A (Automática)**: `bash scripts/deploy-to-aws.sh`
- **Opción B (Manual)**: Seguir PASO 1 - PASO 5 arriba
- **Guía Completa**: Ver `docs/DEPLOYMENT_AWS.md`
- **Troubleshooting**: Ver `docs/TROUBLESHOOTING.md`

**Tiempo estimado**: 40-90 minutos  
**Costo**: $3-4 por hora durante el deployment  
**Status**: Listo para producción académica

¡Adelante! 🚀
