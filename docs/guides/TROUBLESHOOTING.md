# TROUBLESHOOTING Guide - AREP Common Issues

Solutions to common problems and how to diagnose issues.

## Critical Issues

### Docker Container Won't Start

Verify Docker is installed and daemon is running. Check logs with `docker compose logs`.

### Port Already in Use

Check `5173`, `8000`, `5432` and stop blocking processes or change published ports in `docker-compose.yml`.

### Database Connection Failed

Check Postgres container health, `AREP_DATABASE_URL` and restart database if needed.

## Backend Issues

View backend logs: `docker compose logs -f arep-backend`.

Common fixes: rebuild image, verify env vars, check CORS and JWT secret.

## Frontend Issues

Check `VITE_API_BASE_URL` and CORS settings; rebuild frontend when changing config.

## E2E Tests

Install Playwright browsers: `npx playwright install chromium` and ensure backend is running.
