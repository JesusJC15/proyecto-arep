# QUICKSTART - Get AREP Running in 5 Minutes

Fast-track guide for developers who want to try AREP immediately.

## Prerequisites Check (30 seconds)

```bash
docker --version
docker compose --version
```

If not installed, follow `SETUP_GUIDE.md`.

## Install (1 minute)

```bash
git clone https://github.com/JesusJC15/proyecto-arep.git
cd proyecto-arep
```

## Start (2 minutes)

```bash
docker compose up --build -d
docker compose ps
```

Open your browser: `http://localhost:4173`

Login: `ana.patient / demo123` or `dr.suarez / demo123`

## Note: demo pública

Frontend disponible en:
https://arep-production-frontend.s3-website-us-east-1.amazonaws.com/
