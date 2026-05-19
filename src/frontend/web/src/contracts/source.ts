/**
 * Acceptance Criteria:
 * - SourceConnectorResponseSchema validates source connector API responses.
 * - PolicyRuleResponseSchema validates policy rule responses.
 * - PolicyDecisionResponseSchema validates decision responses.
 * - URLCandidateResponseSchema validates URL candidate responses.
 * - CredentialProfileResponseSchema validates credential profile responses.
 * - CredentialValidationRunResponseSchema validates validation run responses.
 * - AdapterRegistryResponseSchema validates adapter registry entries.
 * - All schemas use strict Zod types; no TypeScript `any`.
 */
import { z } from "zod";

export const SourceTypeSchema = z.enum([
  "public_web",
  "search_provider",
  "enrichment_provider",
  "email_verification",
  "outreach_export",
]);

export const ConnectorStatusSchema = z.enum([
  "active",
  "paused",
  "error",
  "disabled",
]);

export const PolicyDecisionSchema = z.enum(["allow", "block", "review"]);

export const CredentialStatusSchema = z.enum([
  "active",
  "expiring",
  "expired",
  "validation_failed",
  "insufficient_scope",
  "revoked",
  "disabled",
]);

export const SourceConnectorResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  source_type: SourceTypeSchema,
  name: z.string(),
  base_url: z.string().nullable(),
  adapter_key: z.string(),
  status: ConnectorStatusSchema,
  config_json: z.string().nullable(),
  rate_limit_per_minute: z.number().nullable(),
  credential_profile_id: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const SourceConnectorCreateSchema = z.object({
  source_type: SourceTypeSchema,
  name: z.string().min(1),
  adapter_key: z.string().min(1),
  base_url: z.string().optional(),
  config_json: z.string().optional(),
  rate_limit_per_minute: z.number().optional(),
  credential_profile_id: z.string().optional(),
});

export const SourceConnectorUpdateSchema = z.object({
  name: z.string().optional(),
  base_url: z.string().optional(),
  status: ConnectorStatusSchema.optional(),
  rate_limit_per_minute: z.number().optional(),
  config_json: z.string().optional(),
  credential_profile_id: z.string().optional(),
});

export const SourceTestResultSchema = z.object({
  adapter_key: z.string(),
  success: z.boolean(),
  latency_ms: z.number().nullable(),
  error: z.string().nullable(),
});

export const PolicyRuleResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  entity_type: z.string(),
  entity_id: z.string().nullable(),
  pattern: z.string().nullable(),
  decision: PolicyDecisionSchema,
  priority: z.number(),
  reason: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const PolicyRuleCreateSchema = z.object({
  entity_type: z.string().min(1),
  pattern: z.string().optional(),
  entity_id: z.string().optional(),
  decision: PolicyDecisionSchema,
  priority: z.number().optional(),
  reason: z.string().optional(),
});

export const PolicyDecisionRequestSchema = z.object({
  operation_type: z.string().min(1),
  url: z.string().optional(),
  source_connector_id: z.string().optional(),
  entity_id: z.string().optional(),
});

export const PolicyDecisionResponseSchema = z.object({
  decision: PolicyDecisionSchema,
  matched_rule_id: z.string().nullable(),
  reason: z.string().nullable(),
});

export const URLCandidateResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  url: z.string(),
  status: z.string(),
  policy_decision: PolicyDecisionSchema.nullable(),
  submitted_at: z.string(),
  reviewed_at: z.string().nullable(),
  reviewer_id: z.string().nullable(),
});

export const CredentialProfileResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  name: z.string(),
  adapter_key: z.string(),
  status: CredentialStatusSchema,
  scopes: z.array(z.string()),
  masked_fingerprint: z.string().nullable(),
  expires_at: z.string().nullable(),
  last_validated_at: z.string().nullable(),
  next_validation_at: z.string().nullable(),
  rotation_due_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const CredentialProfileCreateSchema = z.object({
  name: z.string().min(1),
  adapter_key: z.string().min(1),
  secret_reference: z.string().min(1),
  scopes: z.array(z.string()).optional(),
  expires_at: z.string().optional(),
  rotation_due_at: z.string().optional(),
});

export const CredentialProfileUpdateSchema = z.object({
  name: z.string().optional(),
  status: CredentialStatusSchema.optional(),
  scopes: z.array(z.string()).optional(),
  expires_at: z.string().optional(),
  masked_fingerprint: z.string().optional(),
  rotation_due_at: z.string().optional(),
});

export const CredentialValidationRunResponseSchema = z.object({
  id: z.string().min(1),
  credential_profile_id: z.string().min(1),
  status: z.enum(["passed", "failed"]),
  reason: z.string().nullable(),
  ran_at: z.string(),
});

export const AdapterRegistryResponseSchema = z.object({
  id: z.string().min(1),
  adapter_key: z.string(),
  display_name: z.string(),
  source_type: SourceTypeSchema,
  audit_event_type: z.string(),
  timeout_seconds: z.number(),
  retry_class: z.string(),
  terms_url: z.string().nullable(),
  cost_model: z.string().nullable(),
  is_certified: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type SourceConnectorResponse = z.infer<typeof SourceConnectorResponseSchema>;
export type SourceConnectorCreate = z.infer<typeof SourceConnectorCreateSchema>;
export type SourceConnectorUpdate = z.infer<typeof SourceConnectorUpdateSchema>;
export type SourceTestResult = z.infer<typeof SourceTestResultSchema>;
export type PolicyRuleResponse = z.infer<typeof PolicyRuleResponseSchema>;
export type PolicyRuleCreate = z.infer<typeof PolicyRuleCreateSchema>;
export type PolicyDecisionRequest = z.infer<typeof PolicyDecisionRequestSchema>;
export type PolicyDecisionResponse = z.infer<typeof PolicyDecisionResponseSchema>;
export type URLCandidateResponse = z.infer<typeof URLCandidateResponseSchema>;
export type CredentialProfileResponse = z.infer<typeof CredentialProfileResponseSchema>;
export type CredentialProfileCreate = z.infer<typeof CredentialProfileCreateSchema>;
export type CredentialProfileUpdate = z.infer<typeof CredentialProfileUpdateSchema>;
export type CredentialValidationRunResponse = z.infer<
  typeof CredentialValidationRunResponseSchema
>;
export type AdapterRegistryResponse = z.infer<typeof AdapterRegistryResponseSchema>;

export const SourceConnectorListResponseSchema = z.array(SourceConnectorResponseSchema);
export const PolicyRuleListResponseSchema = z.array(PolicyRuleResponseSchema);
export const URLCandidateListResponseSchema = z.array(URLCandidateResponseSchema);
export const CredentialProfileListResponseSchema = z.array(CredentialProfileResponseSchema);
export const AdapterRegistryListResponseSchema = z.array(AdapterRegistryResponseSchema);
