/**
 * Phase 03 Playwright smoke test.
 *
 * Acceptance Criteria:
 * - Review queue page renders for a pipeline.
 * - ICP config page renders for a pipeline.
 * - Guardrails page renders for a pipeline.
 * - Decision toolbar buttons are present on the review queue page.
 * - ICP config form inputs are visible.
 *
 * Note: These tests run against a real dev server with MSW or backend seeded data.
 * Navigation-only checks work without a backend since pages render their forms.
 */
import { expect, test } from "@playwright/test";

const FAKE_CLIENT_ID = "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5";
const FAKE_PIPELINE_ID = "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6";

const base = `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}`;

test("review queue page renders heading", async ({ page }) => {
  await page.goto(`${base}/review`);
  await expect(page.getByRole("heading", { name: "Review Queue" })).toBeVisible();
});

test("review queue page shows status tabs", async ({ page }) => {
  await page.goto(`${base}/review`);
  await expect(page.getByRole("tab", { name: "Pending" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Approved" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Rejected" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "All" })).toBeVisible();
});

test("ICP config page renders form", async ({ page }) => {
  await page.goto(`${base}/icp-config`);
  await expect(page.getByRole("heading", { name: "ICP Configuration" })).toBeVisible();
  await expect(page.getByTestId("input-vertical")).toBeVisible();
  await expect(page.getByTestId("input-titles")).toBeVisible();
  await expect(page.getByTestId("btn-save-icp")).toBeVisible();
});

test("guardrails page renders heading", async ({ page }) => {
  await page.goto(`${base}/guardrails`);
  await expect(page.getByRole("heading", { name: "Enrichment Guardrails" })).toBeVisible();
});
