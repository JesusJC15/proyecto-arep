#!/bin/bash

# AWS DEPLOYMENT AUTOMATION SCRIPT
# Automatiza los pasos 1-7 de deployment a AWS
# 
# Uso: ./deploy-to-aws.sh
# O: bash deploy-to-aws.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones helper
log_step() {
    echo -e "\n${BLUE}▶ PASO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    exit 1
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================================================
# STEP 1: Verificar Prerequisitos
# ============================================================================

log_step "1: Verificando Prerequisitos"

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI no instalado. Descárgalo de https://awscli.amazonaws.com"
fi
log_success "AWS CLI encontrado: $(aws --version)"

# Verificar Terraform
if ! command -v terraform &> /dev/null; then
    log_error "Terraform no instalado. Descárgalo de https://www.terraform.io/downloads"
fi
log_success "Terraform encontrado: $(terraform --version | head -n1)"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker no instalado. Instálalo de https://www.docker.com"
fi
log_success "Docker encontrado: $(docker --version)"

# Verificar Git
if ! command -v git &> /dev/null; then
    log_error "Git no instalado"
fi
log_success "Git encontrado"

# ============================================================================
# STEP 2: Obtener Configuración
# ============================================================================

log_step "2: Configuración"

read -p "Ingresa tu AWS Profile (default: arep): " AWS_PROFILE
AWS_PROFILE=${AWS_PROFILE:-arep}

read -p "Ingresa AWS Region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

read -p "Ingresa tu AWS Account ID: " AWS_ACCOUNT_ID
if [[ ! $AWS_ACCOUNT_ID =~ ^[0-9]{12}$ ]]; then
    log_error "Account ID debe ser 12 dígitos"
fi

read -p "Ingresa tu IP (para backend acceso): " MY_IP
if [[ ! $MY_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    log_error "IP format inválido"
fi

# Verificar AWS credentials
log_step "3: Verificando AWS Credentials"
if ! aws sts get-caller-identity --profile $AWS_PROFILE &> /dev/null; then
    log_error "No se pueden verificar AWS credentials. Ejecuta: aws configure --profile $AWS_PROFILE"
fi
log_success "AWS credentials verificados"

# ============================================================================
# STEP 4: Crear ECR Repository
# ============================================================================

log_step "4: Creando ECR Repository"

ECR_REPO="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/arep-backend"

if aws ecr describe-repositories --repository-names arep-backend --region $AWS_REGION --profile $AWS_PROFILE &> /dev/null; then
    log_warning "ECR repository ya existe"
else
    aws ecr create-repository \
        --repository-name arep-backend \
        --region $AWS_REGION \
        --profile $AWS_PROFILE > /dev/null
    log_success "ECR repository creado"
fi

# ============================================================================
# STEP 5: Crear Secrets
# ============================================================================

log_step "5: Creando Secrets en AWS Secrets Manager"

# JWT Secret
if ! aws secretsmanager get-secret-value --secret-id arep/jwt-secret --region $AWS_REGION --profile $AWS_PROFILE &> /dev/null; then
    JWT_SECRET=$(openssl rand -base64 32)
    aws secretsmanager create-secret \
        --name arep/jwt-secret \
        --secret-string "$JWT_SECRET" \
        --region $AWS_REGION \
        --profile $AWS_PROFILE > /dev/null
    log_success "JWT secret creado"
else
    log_warning "JWT secret ya existe"
fi

# DB Password
if ! aws secretsmanager get-secret-value --secret-id arep/db-password --region $AWS_REGION --profile $AWS_PROFILE &> /dev/null; then
    DB_PASSWORD=$(openssl rand -base64 16)
    aws secretsmanager create-secret \
        --name arep/db-password \
        --secret-string "$DB_PASSWORD" \
        --region $AWS_REGION \
        --profile $AWS_PROFILE > /dev/null
    log_success "DB password creado"
else
    log_warning "DB password ya existe"
fi

# ============================================================================
# STEP 6: Docker Build & Push
# ============================================================================

log_step "6: Construyendo y publicando imagen Docker"

# Login a ECR
log_warning "Haciendo login en ECR..."
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | \
    docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build backend
log_warning "Construyendo imagen backend..."
cd backend
docker build -t arep-backend:latest .
cd ..

# Tag
docker tag arep-backend:latest $ECR_REPO:latest

# Push
log_warning "Publicando a ECR (esto puede tomar varios minutos)..."
docker push $ECR_REPO:latest
log_success "Imagen publicada"

# ============================================================================
# STEP 7: Terraform Setup
# ============================================================================

log_step "7: Preparando Terraform"

cd infra/aws

# Crear terraform.tfvars
cat > terraform.tfvars << EOF
project_name           = "arep"
environment            = "production"
aws_region             = "$AWS_REGION"
vpc_cidr               = "10.42.0.0/16"
public_subnet_cidr     = "10.42.1.0/24"
private_subnet_a_cidr  = "10.42.10.0/24"
private_subnet_b_cidr  = "10.42.11.0/24"
public_subnet_az       = "${AWS_REGION}a"
private_subnet_a_az    = "${AWS_REGION}a"
private_subnet_b_az    = "${AWS_REGION}b"
backend_ingress_cidrs  = ["${MY_IP}/32"]
db_instance_class      = "db.t3.micro"
db_allocated_storage   = 20
db_storage_type        = "gp3"
backend_container_image = "$ECR_REPO:latest"
EOF

log_success "terraform.tfvars creado"

# Initialize Terraform
log_warning "Inicializando Terraform..."
terraform init

# Validate
log_warning "Validando configuración..."
terraform validate
log_success "Configuración válida"

# Plan
log_warning "Generando plan Terraform..."
terraform plan -out=arep.tfplan

echo -e "\n${YELLOW}⚠️  IMPORTANTE: Revisa el plan arriba antes de continuar${NC}"
read -p "¿Continuar con terraform apply? (sí/no): " -r
if [[ ! $REPLY =~ ^[Ss][Ii]$ ]]; then
    log_error "Deployment cancelado por usuario"
fi

# ============================================================================
# STEP 8: Apply Terraform
# ============================================================================

log_step "8: Desplegando infraestructura en AWS"

log_warning "Aplicando Terraform (esto toma 10-15 minutos)..."
terraform apply arep.tfplan
log_success "Infraestructura desplegada"

# Guardar outputs
terraform output > deployment_info.txt
log_success "Outputs guardados en deployment_info.txt"

# ============================================================================
# STEP 9: Obtener información
# ============================================================================

log_step "9: Información de Deployment"

ALB_DNS=$(terraform output -raw backend_load_balancer_dns)
DB_ENDPOINT=$(terraform output -raw database_endpoint)
CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
SERVICE_NAME=$(terraform output -raw backend_service_name)

echo -e "${GREEN}═════════════════════════════════════════${NC}"
echo "Backend Load Balancer: $ALB_DNS"
echo "Database Endpoint: $DB_ENDPOINT"
echo "ECS Cluster: $CLUSTER_NAME"
echo "ECS Service: $SERVICE_NAME"
echo -e "${GREEN}═════════════════════════════════════════${NC}"

# ============================================================================
# STEP 10: Wait for ECS
# ============================================================================

log_step "10: Esperando que ECS inicie (esto toma 3-5 minutos)"

log_warning "Esperando task deployment..."
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $AWS_REGION \
    --profile $AWS_PROFILE

log_success "ECS service está estable"

# ============================================================================
# STEP 11: Validación
# ============================================================================

log_step "11: Validando Deployment"

log_warning "Probando endpoints..."

# Health check
HEALTH=$(curl -s http://$ALB_DNS/health)
if echo $HEALTH | grep -q "ok"; then
    log_success "Health check: OK"
else
    log_error "Health check falló"
fi

# Ready check
READY=$(curl -s http://$ALB_DNS/ready)
if echo $READY | grep -q "ready"; then
    log_success "Ready check: OK"
else
    log_error "Ready check falló"
fi

# RAG status
RAG=$(curl -s http://$ALB_DNS/rag/status)
if echo $RAG | grep -q "ready"; then
    log_success "RAG status: OK"
else
    log_error "RAG status falló"
fi

# ============================================================================
# FINAL
# ============================================================================

echo -e "\n${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DEPLOYMENT A AWS COMPLETADO${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}URLs IMPORTANTES:${NC}"
echo "Backend API: http://$ALB_DNS"
echo "Database: $DB_ENDPOINT:5432"
echo ""

echo -e "${BLUE}Próximos Pasos:${NC}"
echo "1. Probar en el navegador: http://$ALB_DNS/health"
echo "2. Login de prueba: ana.patient / demo123"
echo "3. Revisar CloudWatch logs: aws logs tail /ecs/arep-production-backend --follow --profile $AWS_PROFILE"
echo ""

echo -e "${YELLOW}Para destruir infraestructura (ahorrar costos):${NC}"
echo "cd infra/aws && terraform destroy --profile $AWS_PROFILE"

cd ../..
