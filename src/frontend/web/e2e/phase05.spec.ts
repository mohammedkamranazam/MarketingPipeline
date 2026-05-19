/**
 * Phase 05 Playwright smoke tests.
 *
 * Acceptance Criteria:
 * - Crawl run monitor page renders heading and New Job button.
 * - Artifact inspector page renders heading and Robots.txt Check panel.
 *
 * Note: These tests run against a real dev server with MSW or backend seeded data.
 * Navigation-only checks work without a backend since pages render their structure.
 */
import { expect, test } from "@playwright/test";

const FAKE_CLIENT_ID = "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5";
const FAKE_PIPELINE_ID = "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6";

const base = `/clients/${FAKE_CLIENT_ID}/pipelines/${FAKE_PIPELINE_ID}`;

test("crawl monitor page renders heading", async ({ page }) => {
  await page.goto(`${base}/crawl`);
  await expect(page.getByRole("heading", { name: "Crawl Job Monitor" })).toBeVisible();
});

test("crawl monitor page has New Job button", async ({ page }) => {
  await page.goto(`${base}/crawl`);
  await expect(page.getByRole("button", { name: "New Job" })).toBeVisible();
});

test("artifact inspector page renders heading", async ({ page }) => {
  await page.goto(`${base}/artifacts`);
  await expect(page.getByRole("heading", { name: "Artifact Inspector" })).toBeVisible();
});

test("artifact inspector page has robots check panel", async ({ page }) => {
  await page.goto(`${base}/artifacts`);
  await expect(page.getByText("Robots.txt Check")).toBeVisible();
  await expect(page.getByRole("button", { name: "Check" })).toBeVisible();
});

test("artifact inspector page has URL input for robots check", async ({ page }) => {
  await page.goto(`${base}/artifacts`);
  await expect(page.getByPlaceholder(/https:\/\/example\.com/)).toBeVisible();
});
