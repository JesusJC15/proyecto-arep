# ✅ AWS DEPLOYMENT CHECKLIST

**Usa este checklist para rastrear tu progreso**

---

## 🔐 PASO 1: AWS Setup (30 min)

- [ ] **1.1** Cuenta AWS creada y accesible
- [ ] **1.2** IAM user "arep-deployer" creado con permisos
- [ ] **1.3** AWS credentials descargados (CSV)
- [ ] **1.4** AWS CLI instalado (`aws --version`)
- [ ] **1.5** AWS CLI configurado (`aws configure --profile arep`)
- [ ] **1.6** Credenciales verificadas (`aws sts get-caller-identity --profile arep`)

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🏗️ PASO 2: Preparar Infraestructura en AWS (20 min)

- [ ] **2.1** ECR repository "arep-backend" creado
- [ ] **2.2** ECR URI guardada en variable `ECR_REPO`
- [ ] **2.3** Secret "arep/jwt-secret" creado en Secrets Manager
- [ ] **2.4** Secret "arep/db-password" creado en Secrets Manager

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🐳 PASO 3: Docker Build & Push (20 min)

- [ ] **3.1** Docker CLI login en ECR exitoso
- [ ] **3.2** Backend image construida (`docker build`)
- [ ] **3.3** Backend image taggeada con ECR URI
- [ ] **3.4** Backend image pushed a ECR (`docker push`)
- [ ] **3.5** Imagen visible en AWS Console → ECR
- [ ] **3.6** (Opcional) Frontend image construida y publicada

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🗂️ PASO 4: Terraform Preparación (15 min)

- [ ] **4.1** Terraform instalado (`terraform --version >= 1.6.0`)
- [ ] **4.2** Archivo `terraform.tfvars` creado con valores correctos
- [ ] **4.3** Terraform inicializado (`terraform init`)
- [ ] **4.4** Configuración validada (`terraform validate`)
- [ ] **4.5** Plan generado (`terraform plan -out=arep.tfplan`)
- [ ] **4.6** Plan revisado (verificar recursos a crear)

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## ⚙️ PASO 5: Desplegar Infraestructura (15 min de espera)

- [ ] **5.1** Terraform apply ejecutado (`terraform apply arep.tfplan`)
- [ ] **5.2** Todos los recursos creados exitosamente (15+ resources)
- [ ] **5.3** Outputs guardados (`terraform output > deployment_info.txt`)
- [ ] **5.4** ALB DNS obtenido
- [ ] **5.5** Database endpoint obtenido
- [ ] **5.6** Verificado en AWS Console que recursos existen

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🔗 PASO 6: Base de Datos (10 min)

- [ ] **6.1** RDS state es "available" (verificar con AWS CLI)
- [ ] **6.2** Database endpoint obtenido
- [ ] **6.3** psql/PostgreSQL client instalado
- [ ] **6.4** Conexión a RDS probada exitosamente
- [ ] **6.5** Database schema está vacía (migraciones se harán en ECS)

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🚀 PASO 7: Desplegar Backend en ECS (15 min de espera)

- [ ] **7.1** Secretos verificados en AWS Secrets Manager
- [ ] **7.2** ECS service update ejecutado (`force-new-deployment`)
- [ ] **7.3** Logs monitoreados (ver "Uvicorn running")
- [ ] **7.4** ECS task alcanzó estado RUNNING
- [ ] **7.5** Task health status es HEALTHY

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## ✅ PASO 8: Validación (10 min)

- [ ] **8.1** `curl http://<ALB_DNS>/health` retorna `{"status":"ok"}`
- [ ] **8.2** `curl http://<ALB_DNS>/ready` retorna `{"status":"ready"}`
- [ ] **8.3** `curl http://<ALB_DNS>/rag/status` retorna corpus info
- [ ] **8.4** Login funciona (`/auth/login` endpoint)
- [ ] **8.5** Flujo completo probado (create → triage → recommendation)
- [ ] **8.6** Base de datos tiene datos (consultations, users, etc.)

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🌐 PASO 9: Frontend (Opcional, 10 min)

- [ ] **9.1** Frontend build completado (`npm run build`)
- [ ] **9.2** Archivos sincronizados a S3 (`aws s3 sync`)
- [ ] **9.3** Frontend accesible en URL de S3
- [ ] **9.4** Frontend puede conectarse a backend API

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 📊 PASO 10: Monitoreo (5 min)

- [ ] **10.1** CloudWatch dashboard creado y visible
- [ ] **10.2** Alarmas configuradas (CPU, Memory, Errors)
- [ ] **10.3** Log groups verificados
- [ ] **10.4** Costos estimados revisados (~$90-110/mes)

**Status**: ⬜ TODO | 🔵 IN PROGRESS | ✅ DONE

---

## 🎯 DEPLOYMENT COMPLETE! 🎉

### URLs Finales a Guardar:

```
Backend API: http://<ALB_DNS>
Frontend: http://<S3_BUCKET>.s3-website-us-east-1.amazonaws.com
Database: <RDS_ENDPOINT>:5432
CloudWatch: https://console.aws.amazon.com/cloudwatch
```

### Próximos Pasos:

- [ ] Configurar DNS personalizado (si tienes dominio)
- [ ] Configurar SSL/HTTPS con ACM
- [ ] Crear plan de backup para RDS
- [ ] Configurar auto-scaling si necesitas
- [ ] Validación clínica con expertos

---

**Tiempo Total Estimado**: 2-3 horas  
**Costo Mensual**: $90-110 USD  
**Nivel de Dificultad**: ⭐⭐⭐ (Intermedio)

**¿Problemas?** Ver [DEPLOYMENT_AWS.md - Troubleshooting](DEPLOYMENT_AWS.md#-troubleshooting)
