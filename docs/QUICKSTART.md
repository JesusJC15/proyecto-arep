# QUICKSTART - Get AREP Running in 5 Minutes

Fast-track guide for developers who want to try AREP immediately.

## Prerequisites Check (30 seconds)

```bash
# Ensure Docker is installed and running
docker --version
docker compose --version
```

If not installed, follow [SETUP_GUIDE.md](SETUP_GUIDE.md#prerequisites).

## Install (1 minute)

```bash
# Clone and enter the repo
git clone https://github.com/JesusJC15/proyecto-arep.git
cd proyecto-arep
```

## Start (2 minutes)

```bash
# Start all services
docker compose up --build -d

# Wait for services to be healthy (check status)
docker compose ps
```

**All services should show "Up (healthy)"**

## Access (30 seconds)

Open your browser:

```
http://localhost:4173
```

**Login with demo credentials**:
- **Patient**: `ana.patient` / `demo123`
- **Professional**: `dr.suarez` / `demo123`

## First Steps

1. **As Patient**:
   - Enter your name, chief complaint (e.g., "chest tightness")
   - Add symptoms (e.g., "shortness of breath", "fatigue")
   - Click "Run Triage"
   - Review recommendation with evidence sources

2. **As Professional**:
   - View escalated cases in "Professional desk"
   - Review triage results and evidence
   - Add notes and close case

## Verify Everything Works

```bash
# Backend health
curl http://localhost:8000/health

# RAG status
curl http://localhost:8000/rag/status

# Run tests
cd backend && python -m pytest -q
cd ../frontend && npm run test:e2e
```

## Stop Services

```bash
# Stop all services (data persists)
docker compose down

# Remove all data (clean slate)
docker compose down -v
```

## Full Documentation

- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)
- **Architecture**: [docs/architecture/README.md](docs/architecture/README.md)
- **Demo Script**: [docs/demo-script.md](docs/demo-script.md)

**Now explore and enjoy!** 🚀
