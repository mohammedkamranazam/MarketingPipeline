/**
 * Acceptance Criteria:
 * - listCrawlJobs(clientId, pipelineId, status?) fetches GET /crawl-jobs with optional filter.
 * - getCrawlJob(clientId, pipelineId, jobId) returns job or null on 404.
 * - createCrawlJob(clientId, pipelineId, payload) POSTs /crawl-jobs.
 * - cancelCrawlJob(clientId, pipelineId, jobId) POSTs /crawl-jobs/:id/cancel.
 * - runCrawlJob(clientId, pipelineId, jobId, url, policyDecision?) POSTs /crawl-jobs/:id/run.
 * - listArtifacts(clientId, pipelineId, artifactType?) fetches GET /artifacts with optional filter.
 * - getArtifact(clientId, pipelineId, artifactId) returns artifact or null on 404.
 * - storeArtifact(clientId, pipelineId, payload) POSTs /artifacts.
 * - checkRobots(clientId, pipelineId, url) POSTs /robots-check.
 * - listBudgets(clientId, pipelineId) fetches GET /budgets.
 * - All responses validated with Zod schemas.
 * - No TypeScript `any`.
 */
import { ApiError, apiFetch } from "./apiClient";
import {
  CrawlArtifactListResponseSchema,
  CrawlArtifactResponseSchema,
  CrawlBudgetListResponseSchema,
  CrawlJobListResponseSchema,
  CrawlJobResponseSchema,
  RobotsCheckResultSchema,
  type ArtifactStoreRequest,
  type CrawlArtifactResponse,
  type CrawlBudgetResponse,
  type CrawlJobCreate,
  type CrawlJobResponse,
  type RobotsCheckResult,
} from "../contracts/crawl";

function base(clientId: string, pipelineId: string): string {
  return `/clients/${clientId}/pipelines/${pipelineId}`;
}

// ── CrawlJob ──────────────────────────────────────────────────────────────────

export async function listCrawlJobs(
  clientId: string,
  pipelineId: string,
  status?: string,
): Promise<CrawlJobResponse[]> {
  const params = status ? `?status=${encodeURIComponent(status)}` : "";
  const data = await apiFetch(`${base(clientId, pipelineId)}/crawl-jobs${params}`);
  return CrawlJobListResponseSchema.parse(data);
}

export async function getCrawlJob(
  clientId: string,
  pipelineId: string,
  jobId: string,
): Promise<CrawlJobResponse | null> {
  try {
    const data = await apiFetch(`${base(clientId, pipelineId)}/crawl-jobs/${jobId}`);
    return CrawlJobResponseSchema.parse(data);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function createCrawlJob(
  clientId: string,
  pipelineId: string,
  payload: CrawlJobCreate,
): Promise<CrawlJobResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/crawl-jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return CrawlJobResponseSchema.parse(data);
}

export async function cancelCrawlJob(
  clientId: string,
  pipelineId: string,
  jobId: string,
): Promise<void> {
  await apiFetch(`${base(clientId, pipelineId)}/crawl-jobs/${jobId}/cancel`, {
    method: "POST",
  });
}

export async function runCrawlJob(
  clientId: string,
  pipelineId: string,
  jobId: string,
  url: string,
  policyDecision?: string,
): Promise<CrawlArtifactResponse> {
  const params = new URLSearchParams({ url });
  if (policyDecision) params.set("policy_decision", policyDecision);
  const data = await apiFetch(
    `${base(clientId, pipelineId)}/crawl-jobs/${jobId}/run?${params.toString()}`,
    { method: "POST" },
  );
  return CrawlArtifactResponseSchema.parse(data);
}

// ── CrawlArtifact ─────────────────────────────────────────────────────────────

export async function listArtifacts(
  clientId: string,
  pipelineId: string,
  artifactType?: string,
): Promise<CrawlArtifactResponse[]> {
  const params = artifactType ? `?artifact_type=${encodeURIComponent(artifactType)}` : "";
  const data = await apiFetch(`${base(clientId, pipelineId)}/artifacts${params}`);
  return CrawlArtifactListResponseSchema.parse(data);
}

export async function getArtifact(
  clientId: string,
  pipelineId: string,
  artifactId: string,
): Promise<CrawlArtifactResponse | null> {
  try {
    const data = await apiFetch(`${base(clientId, pipelineId)}/artifacts/${artifactId}`);
    return CrawlArtifactResponseSchema.parse(data);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function storeArtifact(
  clientId: string,
  pipelineId: string,
  payload: ArtifactStoreRequest,
): Promise<CrawlArtifactResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/artifacts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return CrawlArtifactResponseSchema.parse(data);
}

// ── Robots check ──────────────────────────────────────────────────────────────

export async function checkRobots(
  clientId: string,
  pipelineId: string,
  url: string,
): Promise<RobotsCheckResult> {
  const data = await apiFetch(
    `${base(clientId, pipelineId)}/robots-check?url=${encodeURIComponent(url)}`,
    { method: "POST" },
  );
  return RobotsCheckResultSchema.parse(data);
}

// ── Budgets ───────────────────────────────────────────────────────────────────

export async function listBudgets(
  clientId: string,
  pipelineId: string,
): Promise<CrawlBudgetResponse[]> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/budgets`);
  return CrawlBudgetListResponseSchema.parse(data);
}
