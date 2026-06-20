import { defineConfig, devices } from "@playwright/test";

const API_PORT = process.env.E2E_API_PORT || "8001";
const WEB_PORT = process.env.E2E_WEB_PORT || "3000";

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
      command: `cd ../backend && DATABASE_PROFILE=sqlite-dev DATABASE_URL=sqlite+aiosqlite:///./wfrp_e2e.db LLM_PROVIDER=mock CORS_ORIGINS=http://localhost:${WEB_PORT} .venv/bin/uvicorn app.main:app --port ${API_PORT}`,
      url: `http://localhost:${API_PORT}/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
    {
      command: `npm run dev -- --port ${WEB_PORT}`,
      url: `http://localhost:${WEB_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        NEXT_PUBLIC_API_URL: `http://localhost:${API_PORT}`,
      },
    },
  ],
});
