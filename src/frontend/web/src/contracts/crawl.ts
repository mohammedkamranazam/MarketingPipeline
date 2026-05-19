/**
 * Acceptance Criteria:
 * - CrawlJobResponseSchema validates crawl job API responses.
 * - CrawlArtifactResponseSchema validates artifact responses.
 * - CrawlBudgetResponseSchema validates budget responses.
 * - RobotsCheckResultSchema validates robots check responses.
 * - All schemas use strict Zod types; no TypeScript `any`.
 */
import { z } from "zod";

export const CrawlJobStatusSchema = z.enum([
  "queued",
  "running",
  "paused",
  "failed",
  "retrying",
  "completed",
  "blocked",
  "stale",
  "cancelled",
]);

export const ArtifactTypeSchema = z.enum([
  "html_page",
  "search_result",
  "profile_evidence",
  "provider_response",
  "import_artifact",
]);

export const CrawlJobResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  source_connector_id: z.string().nullable(),
  job_type: z.string(),
  status: CrawlJobStatusSchema,
  idempotency_key: z.string(),
  trigger: z.string(),
  attempt: z.number(),
  max_attempts: z.number(),
  lease_owner: z.string().nullable(),
  lease_expires_at: z.string().nullable(),
  heartbeat_at: z.string().nullable(),
  scheduled_at: z.string(),
  started_at: z.string().nullable(),
  finished_at: z.string().nullable(),
  error_code: z.string().nullable(),
  error_message: z.string().nullable(),
  trace_id: z.string().nullable(),
  rate_limit_per_minute: z.number().nullable(),
  robots_txt_url: z.string().nullable(),
  concurrency_budget: z.number().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const CrawlJobCreateSchema = z.object({
  source_connector_id: z.string().optional(),
  job_type: z.string().optional(),
  trigger: z.string().optional(),
  max_attempts: z.number().optional(),
  rate_limit_per_minute: z.number().optional(),
  robots_txt_url: z.string().optional(),
  concurrency_budget: z.number().optional(),
});

export const CrawlArtifactResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  crawl_job_id: z.string().nullable(),
  source_connector_id: z.string().nullable(),
  seed_lead_row_id: z.string().nullable(),
  artifact_type: ArtifactTypeSchema,
  url: z.string().nullable(),
  storage_key: z.string(),
  content_hash: z.string().nullable(),
  status: z.string(),
  policy_decision: z.string().nullable(),
  mime_type: z.string().nullable(),
  size_bytes: z.number().nullable(),
  raw_metadata_json: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const ArtifactStoreRequestSchema = z.object({
  url: z.string().optional(),
  content: z.string().min(1),
  mime_type: z.string().optional(),
  artifact_type: ArtifactTypeSchema.optional(),
  policy_decision: z.string().optional(),
  crawl_job_id: z.string().optional(),
  source_connector_id: z.string().optional(),
  seed_lead_row_id: z.string().optional(),
});

export const CrawlBudgetResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().nullable(),
  source_connector_id: z.string().nullable(),
  adapter_key: z.string().nullable(),
  budget_type: z.string(),
  max_concurrent: z.number(),
  current_count: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const RobotsCheckResultSchema = z.object({
  url: z.string(),
  allowed: z.boolean(),
  reason: z.string().nullable(),
});

export type CrawlJobResponse = z.infer<typeof CrawlJobResponseSchema>;
export type CrawlJobCreate = z.infer<typeof CrawlJobCreateSchema>;
export type CrawlArtifactResponse = z.infer<typeof CrawlArtifactResponseSchema>;
export type ArtifactStoreRequest = z.infer<typeof ArtifactStoreRequestSchema>;
export type CrawlBudgetResponse = z.infer<typeof CrawlBudgetResponseSchema>;
export type RobotsCheckResult = z.infer<typeof RobotsCheckResultSchema>;

export const CrawlJobListResponseSchema = z.array(CrawlJobResponseSchema);
export const CrawlArtifactListResponseSchema = z.array(CrawlArtifactResponseSchema);
export const CrawlBudgetListResponseSchema = z.array(CrawlBudgetResponseSchema);
