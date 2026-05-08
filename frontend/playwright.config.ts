import { defineConfig } from "@playwright/test";

const reuseExistingServer = !process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "retain-on-failure"
  },
  webServer: [
    {
      command: "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
      cwd: "../backend",
      env: {
        AREP_ENV: "test",
        AREP_DATABASE_URL: "sqlite:///data/e2e.sqlite3",
        AREP_JWT_SECRET: "e2e-secret-key-with-32-bytes-minimum",
        AREP_SEED_DEMO_DATA: "true",
        AREP_CORS_ORIGINS: "http://127.0.0.1:4173"
      },
      port: 8000,
      reuseExistingServer
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 4173",
      cwd: ".",
      env: {
        VITE_API_BASE_URL: "http://127.0.0.1:8000"
      },
      port: 4173,
      reuseExistingServer
    }
  ]
});
