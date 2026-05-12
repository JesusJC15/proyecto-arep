# SETUP GUIDE - AREP Triage Platform

Complete step-by-step guide to set up, configure, and run the AREP platform locally on Windows, macOS, or Linux.

## Prerequisites

### System Requirements

- **Docker Desktop**: Version 4.10+ ([download](https://www.docker.com/products/docker-desktop))
- **Git**: Version 2.30+ ([download](https://git-scm.com))
- **RAM**: Minimum 4GB recommended (8GB for smooth operation)
- **Disk Space**: ~2GB free for Docker images
- **Ports Available**: 4173 (frontend via Docker Compose), 8000 (backend), 5432 (database)
- **Ports Optional**: 5173 (frontend dev server when running Vite directly)

### System-Specific Notes

**Windows**:

- Docker Desktop requires Windows 10 Professional/Enterprise or Windows 11
- WSL2 (Windows Subsystem for Linux 2) backend recommended
- PowerShell or Command Prompt (cmd) for terminal

**macOS**:

- Intel or Apple Silicon (M1/M2/M3) support
- Homebrew recommended for package management

**Linux**:

- Docker Engine 20.10+ required
- Docker Compose installed separately (or use `docker compose`)
- Common on Ubuntu 20.04+, Debian 11+, CentOS 8+

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/JesusJC15/proyecto-arep.git
cd proyecto-arep
```

### Step 2: Verify Docker Installation

```bash
docker --version
docker compose --version
```

Expected output:

```
Docker version 24.0.0, build abc1234
Docker Compose version v2.15.0
```

If Docker is not installed or version is old, download from [docker.com](https://www.docker.com).

### Step 3: Check Port Availability

**Windows (PowerShell)**:

```powershell
# Check if port 5173 is in use:
netstat -ano | findstr :5173

# Check if port 8000 is in use:
netstat -ano | findstr :8000

# Check if port 5432 is in use:
netstat -ano | findstr :5432
```

**macOS/Linux**:

```bash
# Check all three ports for the Compose stack:
lsof -i :4173
lsof -i :8000
lsof -i :5432
```

If ports are in use, stop the blocking process or modify ports in `docker-compose.yml`.

### Step 4: Build and Start Services

```bash
# Start all services in the background
docker compose up --build -d
```

This command:

- Builds Docker images for backend, frontend, and database
- Starts containers in detached mode
- May take 3–5 minutes on first run

### Step 5: Verify All Services Are Running

```bash
# Check service status
docker compose ps
```

Expected output:

```
NAME            STATUS
arep-postgres   Up (healthy)
arep-backend    Up (healthy)
arep-frontend   Up (healthy)
```

If any service is not "Up", see Troubleshooting.

### Step 6: Access the Application

Open your browser and navigate to:

```
http://localhost:4173
```

You should see the AREP Triage Platform login screen.

## Login Credentials

Two demo users are pre-configured:

| User | Password | Role |
|------|----------|------|
| `ana.patient` | `demo123` | Patient |
| `dr.suarez` | `demo123` | Professional/Healthcare Provider |

## Configuration

### Environment Variables

The application uses environment variables defined in `docker-compose.yml`. To customize:

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

1. Edit `.env` with your settings.

2. Restart services to apply changes:

```bash
docker compose down
docker compose up --build -d
```

### Backend Configuration

If you need to configure backend-specific settings:

1. Navigate to `backend/` directory
2. Edit `app/core/settings.py` or pass environment variables
3. Restart the backend container:

```bash
docker compose restart arep-backend
```

### Frontend Configuration

To customize frontend API endpoint:

1. Set `VITE_API_BASE_URL` before building the frontend image or running Vite directly.
2. For local Vite development, export the variable before `npm run dev`:

```bash
export VITE_API_BASE_URL=http://localhost:8000
```

## Verification

### Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

### Check Backend Readiness

```bash
curl http://localhost:8000/ready
```

Expected response:

```json
{"status": "ready"}
```

### Check RAG Status

```bash
curl http://localhost:8000/rag/status
```

Expected response includes corpus info and `status: ready`.

### Run Backend Tests

```bash
cd backend
python -m pytest -q
```

### Run Frontend E2E Tests

```bash
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

## Operational Commands

View logs, stop/restart services and reset database are covered in Troubleshooting.

## Nota sobre despliegue en AWS

El frontend ya está desplegado públicamente en AWS S3 en modo hosting estático y se puede acceder en:

- <https://arep-production-frontend.s3-website-us-east-1.amazonaws.com/>

Este repositorio contiene plantillas y notas para desplegar el backend y la infraestructura en AWS (ver `infra/aws/` y `docs/deployment/`). La configuracion actual es una demo reproducible; para produccion se recomienda revisar [AWS_DEPLOYMENT_QUICK.md](../deployment/AWS_DEPLOYMENT_QUICK.md).

---

**Last Updated**: May 11, 2026
