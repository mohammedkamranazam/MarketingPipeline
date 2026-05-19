/**
 * Phase 04 Playwright smoke tests.
 *
 * Acceptance Criteria:
 * - Source registry page renders heading and Add Connector link.
 * - Policy simulator page renders heading and URL test input.
 * - Credential health page renders heading and Add Credential link.
 *
 * Note: These tests run against a real dev server with MSW or backend seeded data.
 * Navigation-only checks work without a backend since pages render their structure.
 */
import { expect, test } from "@playwright/test";

const FAKE_CLIENT_ID = "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5";
const FAKE_PIPELINE_ID = "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6";

const base = `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}`;

test("source registry page renders heading", async ({ page }) => {
  await page.goto(`${base}/sources`);
  await expect(page.getByRole("heading", { name: "Source Registry" })).toBeVisible();
});

test("source registry page has Add Connector link", async ({ page }) => {
  await page.goto(`${base}/sources`);
  await expect(page.getByRole("link", { name: "Add Connector" })).toBeVisible();
});

test("policy simulator page renders heading", async ({ page }) => {
  await page.goto(`${base}/policy`);
  await expect(page.getByRole("heading", { name: "Policy Simulator" })).toBeVisible();
});

test("policy simulator page has URL input and evaluate button", async ({ page }) => {
  await page.goto(`${base}/policy`);
  await expect(page.getByPlaceholder(/https:\/\/example\.com/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Evaluate" })).toBeVisible();
});

test("credential health page renders heading", async ({ page }) => {
  await page.goto(`${base}/credentials`);
  await expect(page.getByRole("heading", { name: "Credential Health" })).toBeVisible();
});

test("credential health page has Add Credential link", async ({ page }) => {
  await page.goto(`${base}/credentials`);
  await expect(page.getByRole("link", { name: "Add Credential" })).toBeVisible();
});
