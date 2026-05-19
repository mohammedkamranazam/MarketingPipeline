/**
 * Phase 01 Playwright smoke test.
 *
 * Acceptance Criteria:
 * - Navigating to / redirects to /clients.
 * - The client list page renders.
 * - Clicking "New client" opens the create form.
 * - Submitting the create form navigates to the client detail page.
 * - The client detail page has links to Pipelines, Settings, and Users.
 * - Navigating to pipelines shows the pipeline list with "New pipeline" link.
 *
 * Note: This test runs against the real dev server + real backend.
 * The backend must be running with a seeded database for this test to pass fully.
 * In CI without the backend the test validates frontend navigation only.
 */
import { expect, test } from "@playwright/test";

test("/ redirects to /clients", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/clients/);
});

test("client list page renders heading", async ({ page }) => {
  await page.goto("/clients");
  await expect(page.getByRole("heading", { name: "Clients" })).toBeVisible();
});

test("new client link navigates to create form", async ({ page }) => {
  await page.goto("/clients");
  await page.getByRole("link", { name: /new client/i }).click();
  await expect(page).toHaveURL(/\/clients\/new/);
  await expect(page.getByRole("heading", { name: /new client/i })).toBeVisible();
});

test("create form validates empty name", async ({ page }) => {
  await page.goto("/clients/new");
  await page.getByRole("button", { name: /create client/i }).click();
  await expect(page.getByText("Name is required")).toBeVisible();
});

test("404 route renders not found page", async ({ page }) => {
  await page.goto("/this-does-not-exist");
  await expect(page.getByText("404")).toBeVisible();
});
