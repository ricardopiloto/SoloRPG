import { defineConfig, devices } from "@playwright/test";

const API_PORT = process.env.E2E_API_PORT || "8020";
const WEB_PORT = process.env.E2E_WEB_PORT || "3020";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "e2e-admin-pass";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  timeout: 120_000,
  expect: { timeout: 15_000 },
  reporter: [["list"]],
  use: {
    baseURL: `http://localhost:${WEB_PORT}`,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `cd ../backend && DATABASE_URL=sqlite+aiosqlite:///./wfrp_e2e.db APP_ENV=development AUTH_MODE=fixed_admin ADMIN_PASSWORD=${ADMIN_PASSWORD} LLM_PROVIDER=mock EMAIL_PROVIDER=mock JWT_SECRET=e2e-test-secret CORS_ORIGINS=http://localhost:${WEB_PORT} .venv/bin/uvicorn app.main:app --port ${API_PORT}`,
      url: `http://localhost:${API_PORT}/health`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: `NEXT_PUBLIC_API_URL=http://localhost:${API_PORT} NEXT_PUBLIC_APP_ENV=development NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN=false npm run dev -- --port ${WEB_PORT}`,
      url: `http://localhost:${WEB_PORT}`,
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
