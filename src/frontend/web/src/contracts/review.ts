/**
 * Acceptance Criteria:
 * - ReviewItemResponseSchema validates review item API responses.
 * - ReviewDecisionSchema validates decision payloads.
 * - ActiveICPConfigResponseSchema validates ICP config with list fields.
 * - ActiveICPConfigUpsertSchema validates write payloads.
 * - SuppressionRuleResponseSchema and SuppressionRuleCreateSchema are valid.
 * - EnrichmentGuardrailResponseSchema and EnrichmentGuardrailUpsertSchema are valid.
 * - ConfigAuditLogResponseSchema validates audit log entries.
 * - No TypeScript `any`.
 */
import { z } from "zod";

export const ReviewStatusSchema = z.enum([
  "pending",
  "approved",
  "rejected",
  "edited_and_approved",
]);

export const ReviewItemResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  source_document_id: z.string().nullable(),
  source_knowledge_item_id: z.string().nullable(),
  item_type: z.string(),
  content: z.string(),
  evidence_text: z.string(),
  evidence_page: z.number().nullable(),
  confidence: z.number(),
  status: ReviewStatusSchema,
  actor_id: z.string().nullable(),
  actor_note: z.string().nullable(),
  edited_content: z.string().nullable(),
  decided_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const ReviewItemListResponseSchema = z.array(ReviewItemResponseSchema);

export const ReviewDecisionSchema = z.object({
  status: ReviewStatusSchema,
  actor_id: z.string().optional(),
  actor_note: z.string().optional(),
  edited_content: z.string().optional(),
});

export const ActiveICPConfigResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  pipeline_config_version_id: z.string().nullable(),
  vertical: z.string().nullable(),
  target_company_size_min: z.number().nullable(),
  target_company_size_max: z.number().nullable(),
  geographies: z.array(z.string()),
  titles: z.array(z.string()),
  signals: z.array(z.string()),
  exclusions: z.array(z.string()),
  notes: z.string().nullable(),
  activated_by: z.string().nullable(),
  activated_at: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const ActiveICPConfigUpsertSchema = z.object({
  vertical: z.string().optional(),
  target_company_size_min: z.number().optional(),
  target_company_size_max: z.number().optional(),
  geographies: z.array(z.string()).default([]),
  titles: z.array(z.string()).default([]),
  signals: z.array(z.string()).default([]),
  exclusions: z.array(z.string()).default([]),
  notes: z.string().optional(),
  activated_by: z.string().optional(),
});

export const SuppressionRuleCreateSchema = z.object({
  rule_type: z.enum(["domain", "email", "company", "title"]),
  value: z.string().min(1),
  reason: z.string().optional(),
  added_by: z.string().optional(),
});

export const SuppressionRuleResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  rule_type: z.string(),
  value: z.string(),
  reason: z.string().nullable(),
  added_by: z.string().nullable(),
  created_at: z.string(),
});

export const SuppressionRuleListResponseSchema = z.array(SuppressionRuleResponseSchema);

export const EnrichmentGuardrailUpsertSchema = z.object({
  guardrail_type: z.enum([
    "enrichment_provider",
    "email_verification",
    "outreach_export",
  ]),
  enabled: z.boolean(),
  policy_notes: z.string().optional(),
  approved_by: z.string().optional(),
});

export const EnrichmentGuardrailResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  guardrail_type: z.string(),
  enabled: z.boolean(),
  policy_notes: z.string().nullable(),
  approved_by: z.string().nullable(),
  approved_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const EnrichmentGuardrailListResponseSchema = z.array(EnrichmentGuardrailResponseSchema);

export const ConfigAuditLogResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  actor_id: z.string().nullable(),
  action: z.string(),
  entity_type: z.string(),
  entity_id: z.string().nullable(),
  before_snapshot: z.string().nullable(),
  after_snapshot: z.string().nullable(),
  created_at: z.string(),
});

export const ConfigAuditLogListResponseSchema = z.array(ConfigAuditLogResponseSchema);

export type ReviewStatus = z.infer<typeof ReviewStatusSchema>;
export type ReviewItemResponse = z.infer<typeof ReviewItemResponseSchema>;
export type ReviewDecision = z.infer<typeof ReviewDecisionSchema>;
export type ActiveICPConfigResponse = z.infer<typeof ActiveICPConfigResponseSchema>;
export type ActiveICPConfigUpsert = z.infer<typeof ActiveICPConfigUpsertSchema>;
export type SuppressionRuleCreate = z.infer<typeof SuppressionRuleCreateSchema>;
export type SuppressionRuleResponse = z.infer<typeof SuppressionRuleResponseSchema>;
export type EnrichmentGuardrailUpsert = z.infer<typeof EnrichmentGuardrailUpsertSchema>;
export type EnrichmentGuardrailResponse = z.infer<typeof EnrichmentGuardrailResponseSchema>;
export type ConfigAuditLogResponse = z.infer<typeof ConfigAuditLogResponseSchema>;
