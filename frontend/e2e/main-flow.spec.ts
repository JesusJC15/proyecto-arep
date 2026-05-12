import { expect, test } from "@playwright/test";

test("flujo principal paciente y profesional", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Demo paciente" }).click();
  await expect(page.locator(".session-card strong")).toContainText("Ana Torres");
  await expect(page.getByRole("heading", { name: "Captura estructurada de sintomas" })).toBeVisible();

  await page.getByRole("button", { name: "Enviar consulta y ejecutar triage" }).click();
  await expect(page.getByText("La consulta fue enviada y escalada automaticamente al espacio profesional.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Recomendacion y evidencia" })).toBeVisible();
  await expect(page.getByText("Pipeline RAG:")).toBeVisible();
  await expect(page.locator(".evidence-card").first()).toContainText("Score");

  await page.getByRole("button", { name: "Demo profesional" }).click();
  await expect(page.locator(".session-card strong")).toContainText("Dra. Suarez");
  await expect(page.getByRole("heading", { name: "Casos escalados" })).toBeVisible();

  await page.getByRole("button", { name: "Tomar caso" }).click();
  await expect(page.getByText("Caso asignado correctamente a la sesion profesional actual.")).toBeVisible();

  await page.getByRole("button", { name: "Marcar revisado" }).click();
  await expect(page.getByText("Caso marcado como revisado.")).toBeVisible();
  await expect(page.locator(".evidence-card").first()).toContainText("Score");
});
