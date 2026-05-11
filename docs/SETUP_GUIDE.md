# SETUP GUIDE - AREP Triage Platform

Complete step-by-step guide to set up, configure, and run the AREP platform locally on Windows, macOS, or Linux.

## Prerequisites

### System Requirements
- **Docker Desktop**: Version 4.10+ ([download](https://www.docker.com/products/docker-desktop))
- **Git**: Version 2.30+ ([download](https://git-scm.com))
- **RAM**: Minimum 4GB recommended (8GB for smooth operation)
- **Disk Space**: ~2GB free for Docker images
- **Ports Available**: 5173 (frontend), 8000 (backend), 5432 (database)

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
# Check all three ports:
lsof -i :5173
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

If any service is not "Up", see [Troubleshooting](#troubleshooting) below.

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

2. Edit `.env` with your settings:

```env
# Database
AREP_DATABASE_URL=postgresql+psycopg://arep_user:arep_pass@arep-postgres:5432/arep_db

# JWT Authentication
AREP_JWT_SECRET=your-secret-key-change-this-in-production
AREP_JWT_ALGORITHM=HS256
AREP_ACCESS_TOKEN_TTL_MINUTES=60

# CORS (allowed origins)
AREP_CORS_ORIGINS=http://localhost:4173,http://localhost:5173

# RAG Configuration
AREP_RAG_EMBEDDING_PROVIDER=local
AREP_RAG_EMBEDDING_MODEL=tfidf-hash
AREP_RAG_TOP_K=3
AREP_RAG_CHUNK_SIZE=200
AREP_RAG_CHUNK_OVERLAP=20

# Logging
AREP_ENV=development
```

3. Restart services to apply changes:
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

1. Edit `frontend/vite.config.ts` and update `VITE_API_BASE_URL` if needed
2. Or set environment variable before build:
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

Expected response:
```json
{
  "corpus_version": "2026-05-phase4-expanded",
  "documents_in_corpus": 16,
  "chunks_in_index": "...",
  "embedding_provider": "local",
  "embedding_model": "tfidf-hash",
  "status": "ready"
}
```

### Run Backend Tests

```bash
cd backend
python -m pytest -q
```

Expected: All tests pass (✓ marks)

### Run Frontend E2E Tests

```bash
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

Expected: Test suite passes with 1/1 passed

## Operational Commands

### View Logs

```bash
# View all service logs in real-time
docker compose logs -f

# View only backend logs
docker compose logs -f arep-backend

# View only frontend logs
docker compose logs -f arep-frontend

# View only database logs
docker compose logs -f arep-postgres
```

### Stop Services

```bash
# Stop all services (data persists)
docker compose down

# Stop and remove all data (clean reset)
docker compose down -v
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart arep-backend
```

### Reset Database

```bash
# Remove database volume and restart
docker compose down -v
docker compose up -d
```

**Warning**: This deletes all data in the database.

### View Database

Connect to PostgreSQL directly:

```bash
docker compose exec arep-postgres psql -U arep_user -d arep_db
```

Common SQL commands:
```sql
-- List all tables
\dt

-- View consultations
SELECT * FROM consultations;

-- View triage results
SELECT * FROM triage_results;

-- Exit
\q
```

## Common Issues & Quick Fixes

| Issue | Solution |
|-------|----------|
| Port already in use | Kill blocking process or change port in `docker-compose.yml` |
| Docker daemon not running | Start Docker Desktop application |
| Permission denied (Linux) | Run `docker` with `sudo` or add user to `docker` group |
| Services fail to start | Check logs with `docker compose logs` |
| Database connection error | Ensure `AREP_DATABASE_URL` is correct |
| Frontend shows "Cannot reach API" | Check `VITE_API_BASE_URL` in `frontend/vite.config.ts` |

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Next Steps

1. **Explore the Application**: Log in as `ana.patient` and create a consultation
2. **Review the Architecture**: See [docs/architecture/README.md](docs/architecture/README.md)
3. **Read the Documentation**: See [README.md](README.md) for full project overview
4. **Examine Demo Flow**: See [docs/demo-script.md](docs/demo-script.md) for guided walkthrough
5. **Review Knowledge Base**: See [knowledge-base/](knowledge-base/) for clinical content

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review logs: `docker compose logs -f`
3. Check Docker status: `docker compose ps`
4. Consult the [README.md](README.md)

---

**Last Updated**: May 10, 2026  
**Version**: 1.0
