import { expect, test } from "@playwright/test";

const API_PORT = process.env.E2E_API_PORT || "8020";
const API_BASE = `http://localhost:${API_PORT}`;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "e2e-admin-pass";

test.beforeEach(async ({ page }) => {
  const loginRes = await page.request.post(`${API_BASE}/api/auth/login`, {
    data: { email: "admin", password: ADMIN_PASSWORD },
  });
  expect(loginRes.ok()).toBeTruthy();
  const { access_token, user } = await loginRes.json();

  await page.addInitScript(
    ({ token, authUser }) => {
      localStorage.setItem("wfrp_auth_token", token);
      localStorage.setItem("wfrp_auth_user", JSON.stringify(authUser));
    },
    { token: access_token, authUser: user }
  );
});

test("loop principal: auth → pregen → campanha → sessão → roll → recap", async ({ page }) => {
  await page.goto("/character");
  await expect(page.getByRole("button", { name: "Helena Krauss" })).toBeVisible();
  await page.getByRole("button", { name: "Helena Krauss" }).click();
  await page.waitForURL("**/campaigns");

  await page.getByRole("button", { name: /Iniciar sessão/ }).click();
  await page.waitForURL("**/play/**");

  await page.getByRole("button", { name: "Começar" }).click();
  await expect(page.getByText(/carta anônima|O que você faz/i)).toBeVisible();

  const actionInput = page.locator('input[name="action"]');
  await actionInput.fill("e2e-roll");
  await page.getByRole("button", { name: "Enviar" }).click();

  await expect(page.getByRole("button", { name: "Rolar dado" })).toBeVisible();
  await page.getByRole("button", { name: "Rolar dado" }).click();
  await expect(page.locator(".dice-overlay.is-visible")).toBeVisible();
  await expect(page.locator(".dice-overlay.is-visible")).toBeHidden({ timeout: 15_000 });
  await expect(page.getByText(/completa a ação|passos ecoam/i)).toBeVisible({ timeout: 15_000 });
  await expect(actionInput).toBeEnabled();

  await actionInput.fill("e2e-end");
  await page.getByRole("button", { name: "Enviar" }).click();

  await page.waitForURL("**/session/end", { timeout: 30_000 });
  await expect(page.getByRole("heading", { name: "Fim de Sessão" })).toBeVisible();
  await expect(page.getByText(/XP ganho/i)).toBeVisible();
  await expect(page.getByRole("link", { name: "Progressão" })).toBeVisible();
});
