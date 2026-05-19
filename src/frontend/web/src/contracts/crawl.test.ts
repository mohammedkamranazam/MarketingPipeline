/**
 * Contract schema tests for crawl.ts
 */
import { describe, expect, it } from "vitest";
import {
  CrawlArtifactResponseSchema,
  CrawlBudgetResponseSchema,
  CrawlJobResponseSchema,
  RobotsCheckResultSchema,
} from "./crawl";

const NOW = new Date().toISOString();

const BASE_JOB = {
  id: "j1",
  client_id: "cl1",
  pipeline_id: "p1",
  source_connector_id: null,
  job_type: "crawl",
  status: "queued" as const,
  idempotency_key: "crawl:p1:abc123",
  trigger: "api",
  attempt: 0,
  max_attempts: 3,
  lease_owner: null,
  lease_expires_at: null,
  heartbeat_at: null,
  scheduled_at: NOW,
  started_at: null,
  finished_at: null,
  error_code: null,
  error_message: null,
  trace_id: null,
  rate_limit_per_minute: null,
  robots_txt_url: null,
  concurrency_budget: null,
  created_at: NOW,
  updated_at: NOW,
};

describe("CrawlJobResponseSchema", () => {
  it("accepts valid queued job", () => {
    expect(() => CrawlJobResponseSchema.parse(BASE_JOB)).not.toThrow();
  });
  it("accepts running job with timestamps", () => {
    expect(() =>
      CrawlJobResponseSchema.parse({
        ...BASE_JOB,
        status: "running",
        started_at: NOW,
        attempt: 1,
      })
    ).not.toThrow();
  });
  it("rejects invalid status", () => {
    expect(() =>
      CrawlJobResponseSchema.parse({ ...BASE_JOB, status: "unknown" })
    ).toThrow();
  });
});

describe("CrawlArtifactResponseSchema", () => {
  it("accepts valid artifact", () => {
    expect(() =>
      CrawlArtifactResponseSchema.parse({
        id: "a1",
        client_id: "cl1",
        pipeline_id: "p1",
        crawl_job_id: "j1",
        source_connector_id: null,
        seed_lead_row_id: null,
        artifact_type: "html_page",
        url: "https://ex.com",
        storage_key: "artifacts/p1/html_page/a1",
        content_hash: "abc123",
        status: "stored",
        policy_decision: "allow",
        mime_type: "text/html",
        size_bytes: 256,
        raw_metadata_json: null,
        created_at: NOW,
        updated_at: NOW,
      })
    ).not.toThrow();
  });
  it("rejects invalid artifact_type", () => {
    expect(() =>
      CrawlArtifactResponseSchema.parse({
        id: "a1",
        client_id: "cl1",
        pipeline_id: "p1",
        crawl_job_id: null,
        source_connector_id: null,
        seed_lead_row_id: null,
        artifact_type: "screenshot",
        url: null,
        storage_key: "x",
        content_hash: null,
        status: "stored",
        policy_decision: null,
        mime_type: null,
        size_bytes: null,
        raw_metadata_json: null,
        created_at: NOW,
        updated_at: NOW,
      })
    ).toThrow();
  });
});

describe("CrawlBudgetResponseSchema", () => {
  it("accepts valid budget", () => {
    expect(() =>
      CrawlBudgetResponseSchema.parse({
        id: "b1",
        client_id: "cl1",
        pipeline_id: "p1",
        source_connector_id: null,
        adapter_key: null,
        budget_type: "pipeline",
        max_concurrent: 2,
        current_count: 1,
        created_at: NOW,
        updated_at: NOW,
      })
    ).not.toThrow();
  });
});

describe("RobotsCheckResultSchema", () => {
  it("accepts allowed result", () => {
    expect(() =>
      RobotsCheckResultSchema.parse({ url: "https://x.com", allowed: true, reason: null })
    ).not.toThrow();
  });
  it("accepts disallowed result", () => {
    expect(() =>
      RobotsCheckResultSchema.parse({
        url: "https://x.com/private",
        allowed: false,
        reason: "Disallowed by robots.txt",
      })
    ).not.toThrow();
  });
});
