import { expect, test } from "@playwright/test";

test("loop principal: pregen → campanha → sessão → roll → recap", async ({ page }) => {
  await page.goto("/character");
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
