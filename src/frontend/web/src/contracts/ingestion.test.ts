/**
 * Tests for ingestion Zod contracts.
 *
 * Acceptance criteria:
 * - DocumentResponseSchema parses valid document responses.
 * - DocumentResponseSchema throws on missing required fields.
 * - LeadImportBatchResponseSchema parses valid batch responses.
 * - SeedLeadRowResponseSchema parses validation_errors as list of strings.
 * - SeedLeadRowResponseSchema throws on missing required fields.
 */
import { describe, expect, it } from "vitest";
import {
  DocumentResponseSchema,
  LeadImportBatchResponseSchema,
  SeedLeadRowResponseSchema,
} from "./ingestion";

const NOW = new Date().toISOString();

const VALID_DOCUMENT = {
  id: "d1e2f3a4-b5c6-4d7e-8f9a-b0c1d2e3f4a5",
  client_id: "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5",
  pipeline_id: "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6",
  filename: "file.txt",
  original_name: "original.txt",
  mime_type: "text/plain",
  size_bytes: 1024,
  storage_key: "documents/pipe/file.txt",
  status: "parsed",
  error_message: null,
  created_at: NOW,
  updated_at: NOW,
};

describe("DocumentResponseSchema", () => {
  it("parses a valid document", () => {
    const result = DocumentResponseSchema.parse(VALID_DOCUMENT);
    expect(result.id).toBe(VALID_DOCUMENT.id);
    expect(result.status).toBe("parsed");
  });

  it("throws on missing id", () => {
    const { id: _id, ...rest } = VALID_DOCUMENT;
    expect(() => DocumentResponseSchema.parse(rest)).toThrow();
  });

  it("allows missing updated_at", () => {
    const { updated_at: _ua, ...rest } = VALID_DOCUMENT;
    expect(() => DocumentResponseSchema.parse(rest)).not.toThrow();
  });
});

const VALID_BATCH = {
  id: "e2f3a4b5-c6d7-4e8f-9a0b-c1d2e3f4a5b6",
  client_id: "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5",
  pipeline_id: "c3d4e5f6-a7b8-4c9d-0e1f-a2b3c4d5e6f7",
  filename: "leads.csv",
  original_name: "ai_leads.csv",
  mime_type: "text/csv",
  size_bytes: 2048,
  storage_key: "lead_imports/pipe/leads.csv",
  status: "completed",
  total_rows: 3,
  valid_rows: 2,
  error_rows: 1,
  error_message: null,
  created_at: NOW,
  updated_at: NOW,
};

describe("LeadImportBatchResponseSchema", () => {
  it("parses a valid batch", () => {
    const result = LeadImportBatchResponseSchema.parse(VALID_BATCH);
    expect(result.total_rows).toBe(3);
    expect(result.valid_rows).toBe(2);
  });

  it("throws on missing status", () => {
    const { status: _s, ...rest } = VALID_BATCH;
    expect(() => LeadImportBatchResponseSchema.parse(rest)).toThrow();
  });
});

const VALID_ROW = {
  id: "f3a4b5c6-d7e8-4f9a-0b1c-d2e3f4a5b6c7",
  batch_id: "e2f3a4b5-c6d7-4e8f-9a0b-c1d2e3f4a5b6",
  client_id: "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5",
  pipeline_id: "c3d4e5f6-a7b8-4c9d-0e1f-a2b3c4d5e6f7",
  row_index: 0,
  original_first_name: "alice",
  original_last_name: null,
  original_company: "acme",
  original_source: "LinkedIn",
  original_notes: null,
  raw_values: "{}",
  normalized_first_name: "Alice",
  normalized_last_name: null,
  normalized_company: "Acme",
  normalized_source: "LinkedIn",
  status: "valid",
  validation_errors: [],
  is_duplicate: false,
  created_at: NOW,
};

describe("SeedLeadRowResponseSchema", () => {
  it("parses a valid row", () => {
    const result = SeedLeadRowResponseSchema.parse(VALID_ROW);
    expect(result.validation_errors).toEqual([]);
    expect(result.is_duplicate).toBe(false);
  });

  it("parses validation_errors as array", () => {
    const row = { ...VALID_ROW, validation_errors: ["first_name is required"] };
    const result = SeedLeadRowResponseSchema.parse(row);
    expect(result.validation_errors).toHaveLength(1);
  });

  it("throws on missing row_index", () => {
    const { row_index: _r, ...rest } = VALID_ROW;
    expect(() => SeedLeadRowResponseSchema.parse(rest)).toThrow();
  });
});
