/**
 * Phase 02 Playwright smoke test.
 *
 * Acceptance Criteria:
 * - Document list page renders for a pipeline.
 * - Upload document button is visible.
 * - Seed lead import list page renders for a pipeline.
 * - Upload CSV/XLSX button is visible.
 *
 * Note: These tests run against a real dev server.
 * Full CRUD tests require a running backend with seeded data.
 * Navigation-only smoke tests work without a backend.
 */
import { expect, test } from "@playwright/test";

const FAKE_CLIENT_ID = "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5";
const FAKE_PIPELINE_ID = "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6";

test("document list page renders", async ({ page }) => {
  await page.goto(
    `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}/documents`,
  );
  await expect(page.getByRole("heading", { name: "Documents" })).toBeVisible();
});

test("document list page shows upload button", async ({ page }) => {
  await page.goto(
    `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}/documents`,
  );
  await expect(
    page.getByRole("button", { name: /upload document/i }),
  ).toBeVisible();
});

test("lead import list page renders", async ({ page }) => {
  await page.goto(
    `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}/lead-imports`,
  );
  await expect(
    page.getByRole("heading", { name: /seed lead imports/i }),
  ).toBeVisible();
});

test("lead import list page shows upload button", async ({ page }) => {
  await page.goto(
    `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}/lead-imports`,
  );
  await expect(
    page.getByRole("button", { name: /upload csv/i }),
  ).toBeVisible();
});
