# TROUBLESHOOTING Guide - AREP Common Issues

Solutions to common problems and how to diagnose issues.

---

## 🔴 Critical Issues

### 1. Docker Container Won't Start

**Symptoms**:
- `docker compose up` fails or containers exit immediately
- Error: `docker: command not found`
- Docker daemon is not running

**Solutions**:

a) **Verify Docker is installed**:
```bash
docker --version
```
If not installed, download from [docker.com](https://www.docker.com)

b) **Ensure Docker daemon is running**:
- **Windows/macOS**: Open Docker Desktop application
- **Linux**: Start with `sudo systemctl start docker`

c) **Check Docker permissions** (Linux):
```bash
sudo usermod -aG docker $USER
# Log out and back in, or:
newgrp docker
```

d) **View detailed error logs**:
```bash
docker compose logs
docker compose logs arep-backend
docker compose logs arep-frontend
docker compose logs arep-postgres
```

### 2. Port Already in Use

**Symptoms**:
- Error: `bind: address already in use` or `Port ... is already allocated`
- Services fail to start

**Affected Ports**:
- `5173` - Frontend dev server
- `8000` - Backend API
- `5432` - PostgreSQL database

**Solutions**:

a) **Find and stop the blocking process** (Windows PowerShell):
```powershell
# Find process using port 8000
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($process) {
  Stop-Process -Id $process.OwningProcess -Force
}
```

b) **macOS/Linux**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill process (replace 12345 with PID)
kill -9 12345
```

c) **Change ports in docker-compose.yml**:
```yaml
services:
  arep-frontend:
    ports:
      - "5173:5173"  # Change first 5173 to another port

  arep-backend:
    ports:
      - "8000:8000"  # Change first 8000 to another port

  arep-postgres:
    ports:
      - "5432:5432"  # Change first 5432 to another port
```

Then restart:
```bash
docker compose down
docker compose up --build -d
```

### 3. Database Connection Failed

**Symptoms**:
- Backend logs show: `sqlalchemy.exc.OperationalError` or `connection refused`
- Error: `could not connect to server: Connection refused`

**Solutions**:

a) **Check database is running**:
```bash
docker compose ps arep-postgres
# Should show "Up (healthy)"
```

b) **Verify PostgreSQL is ready**:
```bash
docker compose logs arep-postgres | grep "database system is ready"
```

c) **Check database environment variables**:
```bash
# Verify AREP_DATABASE_URL is set correctly
docker compose config | grep AREP_DATABASE_URL
```

d) **Reset database**:
```bash
docker compose down -v
docker compose up --build -d
```

This removes and recreates the database from scratch.

---

## 🟠 Backend Issues

### 4. Backend Logs Show Errors

**Solutions**:

a) **View full error logs**:
```bash
docker compose logs -f arep-backend
```

b) **Common errors**:

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Missing dependency | Rebuild: `docker compose up --build` |
| `CORS error` | Frontend URL not in CORS_ORIGINS | Update `AREP_CORS_ORIGINS` in `.env` |
| `JWT error` | Bad token or secret | Restart backend or clear cookies |
| `FileNotFoundError` | Knowledge base not found | Check `knowledge-base/` directory exists |

c) **Rebuild backend container**:
```bash
docker compose build --no-cache arep-backend
docker compose up -d arep-backend
```

### 5. API Endpoint Returns 404

**Symptoms**:
- Error: `HTTP 404 Not Found`
- Endpoint doesn't exist or returns unexpected response

**Solutions**:

a) **Verify endpoint exists**:
```bash
# Check health endpoint
curl http://localhost:8000/health

# List all available endpoints (if OpenAPI available)
curl http://localhost:8000/docs
```

b) **Verify request method and format**:
```bash
# Correct: POST request
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ana.patient","password":"demo123"}'

# Wrong: GET request will fail
curl http://localhost:8000/auth/login
```

c) **Check backend is responding**:
```bash
curl -v http://localhost:8000/health
```

### 6. Triage Engine Not Running

**Symptoms**:
- Consultation created but triage fails
- Error: `Triage execution failed` or timeout

**Solutions**:

a) **Check RAG service is ready**:
```bash
curl http://localhost:8000/rag/status
```

Should return:
```json
{"status": "ready"}
```

b) **Check knowledge base is loaded**:
```bash
curl http://localhost:8000/rag/status | grep corpus_version
```

c) **Restart backend**:
```bash
docker compose restart arep-backend
```

d) **View detailed logs**:
```bash
docker compose logs -f arep-backend | grep -i triage
```

---

## 🔵 Frontend Issues

### 7. Frontend Shows "Cannot Reach API"

**Symptoms**:
- CORS error in browser console
- Network requests fail with 403 or connection refused
- Blank page or error message: "Failed to fetch"

**Solutions**:

a) **Check backend is running**:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "ok"}
```

b) **Fix frontend API configuration**:
```bash
# Open frontend/vite.config.ts
# Ensure VITE_API_BASE_URL is set correctly
```

c) **Update CORS in backend** (`.env`):
```bash
AREP_CORS_ORIGINS=http://localhost:4173,http://localhost:5173
```

d) **Rebuild and restart frontend**:
```bash
docker compose build --no-cache arep-frontend
docker compose up -d arep-frontend
```

### 8. Login Fails

**Symptoms**:
- Credentials rejected or invalid
- Error: `Unauthorized` or `Invalid credentials`

**Solutions**:

a) **Verify credentials** (demo users):
```
Patient: ana.patient / demo123
Professional: dr.suarez / demo123
```

b) **Check JWT secret matches**:
```bash
# If you changed JWT_SECRET, reset database
docker compose down -v
docker compose up --build -d
```

c) **Clear browser cache/cookies**:
- Open DevTools (F12)
- Go to Application → Cookies
- Delete all cookies for `localhost`
- Reload page

d) **Check backend logs**:
```bash
docker compose logs arep-backend | grep -i auth
```

### 9. E2E Tests Fail

**Symptoms**:
- Playwright tests time out or fail
- Error: `Cannot find element` or `Page timed out`

**Solutions**:

a) **Install Playwright browsers**:
```bash
cd frontend
npx playwright install chromium
```

b) **Ensure backend is running**:
```bash
docker compose ps arep-backend
# Should show "Up (healthy)"
```

c) **Run tests with verbose output**:
```bash
cd frontend
npm run test:e2e -- --debug
```

d) **Update baseURL if needed**:
Edit `frontend/playwright.config.ts`:
```typescript
export default defineConfig({
  use: {
    baseURL: 'http://localhost:4173',  // Verify this is correct
  },
});
```

e) **Rebuild frontend**:
```bash
docker compose up --build arep-frontend
```

---

## 🟡 Database Issues

### 10. Database Performance Slow

**Symptoms**:
- Queries take > 2 seconds
- Triage execution times out

**Solutions**:

a) **Check database size**:
```bash
docker compose exec arep-postgres psql -U arep_user -d arep_db -c "\db+"
```

b) **Check running queries**:
```bash
docker compose exec arep-postgres psql -U arep_user -d arep_db -c \
  "SELECT * FROM pg_stat_activity;"
```

c) **Restart database**:
```bash
docker compose restart arep-postgres
```

d) **Rebuild with more resources**:
Edit `docker-compose.yml`:
```yaml
arep-postgres:
  environment:
    POSTGRES_SHARED_BUFFERS: "256MB"  # Increase from 128MB
```

### 11. Database Disk Full

**Symptoms**:
- Error: `no space left on device`
- Cannot insert new records

**Solutions**:

a) **Check Docker disk usage**:
```bash
docker system df
```

b) **Clean up unused images and volumes**:
```bash
docker system prune -a --volumes
```

c) **Remove and recreate database**:
```bash
docker compose down -v
docker compose up --build -d
```

---

## 🟢 Performance Issues

### 12. High Memory Usage

**Symptoms**:
- Docker containers consuming > 2GB RAM
- System becomes unresponsive

**Solutions**:

a) **Check memory usage**:
```bash
docker stats
```

b) **Limit memory per container** in `docker-compose.yml`:
```yaml
arep-backend:
  deploy:
    resources:
      limits:
        memory: 512M

arep-frontend:
  deploy:
    resources:
      limits:
        memory: 256M

arep-postgres:
  deploy:
    resources:
      limits:
        memory: 768M
```

c) **Rebuild with limits**:
```bash
docker compose down
docker compose up --build -d
```

### 13. RAG Retrieval Slow

**Symptoms**:
- Triage takes > 5 seconds
- RAG queries slow

**Solutions**:

a) **Check RAG status**:
```bash
curl http://localhost:8000/rag/status
```

b) **Reduce chunk count** in `backend/app/core/settings.py`:
```python
RAG_TOP_K = 3  # Default
# Reduce to 2 or 1 for faster retrieval
```

c) **Rebuild RAG index**:
```bash
docker compose exec arep-backend python -m app.main --force-reindex
# Or set environment variable
docker compose exec arep-backend bash -c \
  "AREP_RAG_FORCE_REINDEX=true python -m app.main"
```

---

## 🔍 Diagnostic Commands

### View All Logs

```bash
# Real-time all logs
docker compose logs -f

# Only errors
docker compose logs | grep -i error

# Specific service
docker compose logs -f arep-backend
```

### Check Service Health

```bash
# All services
docker compose ps

# Specific service
docker compose exec arep-backend curl http://localhost:8000/health
```

### Test Connectivity

```bash
# Frontend → Backend
docker compose exec arep-frontend curl http://arep-backend:8000/health

# Backend → Database
docker compose exec arep-backend python -c \
  "import psycopg; print(psycopg.connect('postgresql://arep_user:arep_pass@arep-postgres/arep_db'))"
```

### Access Containers Directly

```bash
# Access backend shell
docker compose exec arep-backend bash

# Access database CLI
docker compose exec arep-postgres psql -U arep_user -d arep_db

# Access frontend directory
docker compose exec arep-frontend bash
```

---

## 📞 Still Stuck?

1. **Gather diagnostic information**:
```bash
docker compose ps
docker compose logs > logs.txt
docker system df
```

2. **Check the README**: [README.md](../README.md)
3. **Review the Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
4. **Search GitHub Issues**: [JesusJC15/proyecto-arep/issues](https://github.com/JesusJC15/proyecto-arep/issues)

---

**Last Updated**: May 10, 2026  
**Version**: 1.0
