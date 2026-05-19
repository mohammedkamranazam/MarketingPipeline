/**
 * Acceptance Criteria:
 * - listReviewItems(clientId, pipelineId, status?) fetches GET /review-items with optional ?status= filter.
 * - getReviewItem(clientId, pipelineId, itemId) fetches a single review item.
 * - decideReviewItem(clientId, pipelineId, itemId, decision) POSTs to /decide.
 * - getICPConfig(clientId, pipelineId) fetches GET /icp-config; returns null on 404.
 * - upsertICPConfig(clientId, pipelineId, payload) PUTs /icp-config.
 * - listSuppressionRules(clientId, pipelineId) fetches GET /suppression-rules.
 * - addSuppressionRule(clientId, pipelineId, payload) POSTs /suppression-rules.
 * - deleteSuppressionRule(clientId, pipelineId, ruleId) DELETEs /suppression-rules/:id.
 * - listGuardrails(clientId, pipelineId) fetches GET /guardrails.
 * - upsertGuardrail(clientId, pipelineId, payload) PUTs /guardrails.
 * - listAuditLog(clientId, pipelineId) fetches GET /audit-log.
 * - All responses validated with Zod schemas.
 * - No TypeScript `any`.
 */
import { ApiError, apiFetch } from "./apiClient";
import {
  ActiveICPConfigResponseSchema,
  ActiveICPConfigUpsertSchema,
  ConfigAuditLogListResponseSchema,
  EnrichmentGuardrailListResponseSchema,
  EnrichmentGuardrailResponseSchema,
  ReviewItemListResponseSchema,
  ReviewItemResponseSchema,
  SuppressionRuleListResponseSchema,
  SuppressionRuleResponseSchema,
  type ActiveICPConfigResponse,
  type ActiveICPConfigUpsert,
  type ConfigAuditLogResponse,
  type EnrichmentGuardrailResponse,
  type EnrichmentGuardrailUpsert,
  type ReviewDecision,
  type ReviewItemResponse,
  type SuppressionRuleCreate,
  type SuppressionRuleResponse,
} from "../contracts/review";

function base(clientId: string, pipelineId: string): string {
  return `/clients/${clientId}/pipelines/${pipelineId}`;
}

export async function listReviewItems(
  clientId: string,
  pipelineId: string,
  status?: string,
): Promise<ReviewItemResponse[]> {
  const url = status
    ? `${base(clientId, pipelineId)}/review-items?status=${encodeURIComponent(status)}`
    : `${base(clientId, pipelineId)}/review-items`;
  const data = await apiFetch<unknown>(url);
  return ReviewItemListResponseSchema.parse(data);
}

export async function getReviewItem(
  clientId: string,
  pipelineId: string,
  itemId: string,
): Promise<ReviewItemResponse> {
  const data = await apiFetch<unknown>(
    `${base(clientId, pipelineId)}/review-items/${itemId}`,
  );
  return ReviewItemResponseSchema.parse(data);
}

export async function decideReviewItem(
  clientId: string,
  pipelineId: string,
  itemId: string,
  decision: ReviewDecision,
): Promise<ReviewItemResponse> {
  const data = await apiFetch<unknown>(
    `${base(clientId, pipelineId)}/review-items/${itemId}/decide`,
    { method: "POST", body: JSON.stringify(decision) },
  );
  return ReviewItemResponseSchema.parse(data);
}

export async function getICPConfig(
  clientId: string,
  pipelineId: string,
): Promise<ActiveICPConfigResponse | null> {
  try {
    const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/icp-config`);
    return ActiveICPConfigResponseSchema.parse(data);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function upsertICPConfig(
  clientId: string,
  pipelineId: string,
  payload: ActiveICPConfigUpsert,
): Promise<ActiveICPConfigResponse> {
  const body = ActiveICPConfigUpsertSchema.parse(payload);
  const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/icp-config`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
  return ActiveICPConfigResponseSchema.parse(data);
}

export async function listSuppressionRules(
  clientId: string,
  pipelineId: string,
): Promise<SuppressionRuleResponse[]> {
  const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/suppression-rules`);
  return SuppressionRuleListResponseSchema.parse(data);
}

export async function addSuppressionRule(
  clientId: string,
  pipelineId: string,
  payload: SuppressionRuleCreate,
): Promise<SuppressionRuleResponse> {
  const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/suppression-rules`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return SuppressionRuleResponseSchema.parse(data);
}

export async function deleteSuppressionRule(
  clientId: string,
  pipelineId: string,
  ruleId: string,
): Promise<void> {
  await apiFetch<void>(`${base(clientId, pipelineId)}/suppression-rules/${ruleId}`, {
    method: "DELETE",
  });
}

export async function listGuardrails(
  clientId: string,
  pipelineId: string,
): Promise<EnrichmentGuardrailResponse[]> {
  const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/guardrails`);
  return EnrichmentGuardrailListResponseSchema.parse(data);
}

export async function upsertGuardrail(
  clientId: string,
  pipelineId: string,
  payload: EnrichmentGuardrailUpsert,
): Promise<EnrichmentGuardrailResponse> {
  const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/guardrails`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  return EnrichmentGuardrailResponseSchema.parse(data);
}

export async function listAuditLog(
  clientId: string,
  pipelineId: string,
): Promise<ConfigAuditLogResponse[]> {
  const data = await apiFetch<unknown>(`${base(clientId, pipelineId)}/audit-log`);
  return ConfigAuditLogListResponseSchema.parse(data);
}
