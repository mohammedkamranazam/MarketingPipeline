/**
 * Acceptance Criteria:
 * - listCrawlJobs returns array of CrawlJobResponse.
 * - getCrawlJob returns job or null on 404.
 * - createCrawlJob returns 201 CrawlJobResponse.
 * - cancelCrawlJob completes without error on 204.
 * - runCrawlJob returns CrawlArtifactResponse.
 * - listArtifacts returns array of CrawlArtifactResponse.
 * - getArtifact returns artifact or null on 404.
 * - storeArtifact returns 201 CrawlArtifactResponse.
 * - checkRobots returns allowed=true for normal URLs and false for /private paths.
 * - listBudgets returns array of CrawlBudgetResponse.
 */
import { describe, expect, it } from "vitest";
import {
  FIXTURE_ARTIFACT,
  FIXTURE_BUDGET,
  FIXTURE_CRAWL_JOB,
  FIXTURE_PIPELINE_A,
} from "../test/msw/handlers";
import {
  cancelCrawlJob,
  checkRobots,
  createCrawlJob,
  getArtifact,
  getCrawlJob,
  listArtifacts,
  listBudgets,
  listCrawlJobs,
  runCrawlJob,
  storeArtifact,
} from "./crawlService";

const CLIENT_ID = FIXTURE_CRAWL_JOB.client_id;
const PIPELINE_ID = FIXTURE_PIPELINE_A.id;

describe("listCrawlJobs", () => {
  it("returns array of crawl jobs", async () => {
    const jobs = await listCrawlJobs(CLIENT_ID, PIPELINE_ID);
    expect(jobs).toHaveLength(1);
    expect(jobs.at(0)?.id).toBe(FIXTURE_CRAWL_JOB.id);
    expect(jobs.at(0)?.status).toBe("queued");
  });

  it("filters by status query param", async () => {
    const jobs = await listCrawlJobs(CLIENT_ID, PIPELINE_ID, "queued");
    expect(jobs).toHaveLength(1);
  });
});

describe("getCrawlJob", () => {
  it("returns a crawl job by id", async () => {
    const job = await getCrawlJob(CLIENT_ID, PIPELINE_ID, FIXTURE_CRAWL_JOB.id);
    expect(job).not.toBeNull();
    expect(job?.id).toBe(FIXTURE_CRAWL_JOB.id);
  });

  it("returns null on 404", async () => {
    const job = await getCrawlJob(CLIENT_ID, PIPELINE_ID, "nonexistent-id");
    expect(job).toBeNull();
  });
});

describe("createCrawlJob", () => {
  it("creates a crawl job and returns 201 response", async () => {
    const job = await createCrawlJob(CLIENT_ID, PIPELINE_ID, { job_type: "crawl" });
    expect(job.id).toBe(FIXTURE_CRAWL_JOB.id);
    expect(job.status).toBe("queued");
  });
});

describe("cancelCrawlJob", () => {
  it("resolves without error on 204", async () => {
    await expect(
      cancelCrawlJob(CLIENT_ID, PIPELINE_ID, FIXTURE_CRAWL_JOB.id),
    ).resolves.toBeUndefined();
  });
});

describe("runCrawlJob", () => {
  it("returns CrawlArtifactResponse after running the job", async () => {
    const artifact = await runCrawlJob(
      CLIENT_ID,
      PIPELINE_ID,
      FIXTURE_CRAWL_JOB.id,
      "https://example.com/page",
    );
    expect(artifact.id).toBe(FIXTURE_ARTIFACT.id);
    expect(artifact.artifact_type).toBe("html_page");
  });

  it("passes policy_decision param when provided", async () => {
    const artifact = await runCrawlJob(
      CLIENT_ID,
      PIPELINE_ID,
      FIXTURE_CRAWL_JOB.id,
      "https://example.com/page",
      "allow",
    );
    expect(artifact.id).toBe(FIXTURE_ARTIFACT.id);
  });
});

describe("listArtifacts", () => {
  it("returns array of artifacts", async () => {
    const artifacts = await listArtifacts(CLIENT_ID, PIPELINE_ID);
    expect(artifacts).toHaveLength(1);
    expect(artifacts.at(0)?.id).toBe(FIXTURE_ARTIFACT.id);
  });

  it("filters by artifact_type query param", async () => {
    const artifacts = await listArtifacts(CLIENT_ID, PIPELINE_ID, "html_page");
    expect(artifacts).toHaveLength(1);
  });
});

describe("getArtifact", () => {
  it("returns artifact by id", async () => {
    const artifact = await getArtifact(CLIENT_ID, PIPELINE_ID, FIXTURE_ARTIFACT.id);
    expect(artifact).not.toBeNull();
    expect(artifact?.id).toBe(FIXTURE_ARTIFACT.id);
    expect(artifact?.content_hash).toBe("deadbeefdeadbeef");
  });

  it("returns null on 404", async () => {
    const artifact = await getArtifact(CLIENT_ID, PIPELINE_ID, "nonexistent-id");
    expect(artifact).toBeNull();
  });
});

describe("storeArtifact", () => {
  it("stores an artifact and returns 201 response", async () => {
    const artifact = await storeArtifact(CLIENT_ID, PIPELINE_ID, {
      content: "<html>test</html>",
      mime_type: "text/html",
      artifact_type: "html_page",
      url: "https://example.com/test",
    });
    expect(artifact.id).toBe(FIXTURE_ARTIFACT.id);
    expect(artifact.artifact_type).toBe("html_page");
  });
});

describe("checkRobots", () => {
  it("returns allowed=true for normal URL", async () => {
    const result = await checkRobots(CLIENT_ID, PIPELINE_ID, "https://example.com/page");
    expect(result.allowed).toBe(true);
    expect(result.reason).toBeNull();
  });

  it("returns allowed=false for /private path", async () => {
    const result = await checkRobots(CLIENT_ID, PIPELINE_ID, "https://example.com/private/data");
    expect(result.allowed).toBe(false);
    expect(result.reason).toMatch(/disallowed/i);
  });
});

describe("listBudgets", () => {
  it("returns array of budgets", async () => {
    const budgets = await listBudgets(CLIENT_ID, PIPELINE_ID);
    expect(budgets).toHaveLength(1);
    expect(budgets.at(0)?.id).toBe(FIXTURE_BUDGET.id);
    expect(budgets.at(0)?.budget_type).toBe("pipeline");
    expect(budgets.at(0)?.max_concurrent).toBe(2);
  });
});
