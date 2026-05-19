/**
 * Acceptance Criteria:
 * - DocumentResponseSchema validates document upload and list responses.
 * - LeadImportBatchResponseSchema validates lead import batch responses.
 * - SeedLeadRowResponseSchema validates individual seed lead row responses.
 * - ExtractedKnowledgeItemResponseSchema validates knowledge item responses.
 * - All id fields use z.string().min(1) for MSW/test compatibility.
 * - validation_errors on SeedLeadRowResponse is list[string].
 * - No TypeScript `any`.
 */
import { z } from "zod";

export const DocumentResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  filename: z.string(),
  original_name: z.string(),
  mime_type: z.string(),
  size_bytes: z.number(),
  storage_key: z.string(),
  status: z.string(),
  error_message: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string().optional(),
});

export const DocumentListResponseSchema = z.array(DocumentResponseSchema);

export const ExtractedKnowledgeItemResponseSchema = z.object({
  id: z.string().min(1),
  document_id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  item_type: z.string(),
  content: z.string(),
  evidence_text: z.string(),
  evidence_page: z.number().nullable(),
  confidence: z.number(),
  status: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const KnowledgeItemListResponseSchema = z.array(ExtractedKnowledgeItemResponseSchema);

export const LeadImportBatchResponseSchema = z.object({
  id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  filename: z.string(),
  original_name: z.string(),
  mime_type: z.string(),
  size_bytes: z.number(),
  storage_key: z.string(),
  status: z.string(),
  total_rows: z.number(),
  valid_rows: z.number(),
  error_rows: z.number(),
  error_message: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const LeadImportBatchListResponseSchema = z.array(LeadImportBatchResponseSchema);

export const SeedLeadRowResponseSchema = z.object({
  id: z.string().min(1),
  batch_id: z.string().min(1),
  client_id: z.string().min(1),
  pipeline_id: z.string().min(1),
  row_index: z.number(),
  original_first_name: z.string().nullable(),
  original_last_name: z.string().nullable(),
  original_company: z.string().nullable(),
  original_source: z.string().nullable(),
  original_notes: z.string().nullable(),
  raw_values: z.string(),
  normalized_first_name: z.string().nullable(),
  normalized_last_name: z.string().nullable(),
  normalized_company: z.string().nullable(),
  normalized_source: z.string().nullable(),
  status: z.string(),
  validation_errors: z.array(z.string()),
  is_duplicate: z.boolean(),
  created_at: z.string(),
});

export const SeedLeadRowListResponseSchema = z.array(SeedLeadRowResponseSchema);

export type DocumentResponse = z.infer<typeof DocumentResponseSchema>;
export type ExtractedKnowledgeItemResponse = z.infer<
  typeof ExtractedKnowledgeItemResponseSchema
>;
export type LeadImportBatchResponse = z.infer<typeof LeadImportBatchResponseSchema>;
export type SeedLeadRowResponse = z.infer<typeof SeedLeadRowResponseSchema>;
