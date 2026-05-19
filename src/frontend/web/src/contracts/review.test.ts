/**
 * Tests for Phase 03 review contracts (Zod schemas).
 *
 * Acceptance criteria tested:
 * - ReviewItemResponseSchema parses valid review item response.
 * - ReviewDecisionSchema parses approve, reject, and edited_and_approved.
 * - ReviewDecisionSchema accepts optional fields.
 * - ActiveICPConfigResponseSchema parses valid ICP config with list fields.
 * - ActiveICPConfigUpsertSchema parses write payload with defaults.
 * - SuppressionRuleCreateSchema validates rule_type enum.
 * - SuppressionRuleResponseSchema parses valid suppression rule.
 * - EnrichmentGuardrailUpsertSchema validates guardrail_type enum.
 * - EnrichmentGuardrailResponseSchema parses valid guardrail.
 * - ConfigAuditLogResponseSchema parses valid audit log entry.
 * - Schemas reject missing required fields.
 */
import { describe, expect, it } from "vitest";
import {
  ActiveICPConfigResponseSchema,
  ActiveICPConfigUpsertSchema,
  ConfigAuditLogResponseSchema,
  EnrichmentGuardrailResponseSchema,
  EnrichmentGuardrailUpsertSchema,
  ReviewDecisionSchema,
  ReviewItemResponseSchema,
  SuppressionRuleCreateSchema,
  SuppressionRuleResponseSchema,
} from "./review";

const NOW = new Date().toISOString();

describe("ReviewItemResponseSchema", () => {
  const valid = {
    id: "a1a1a1a1-b2b2-4c3c-d4d4-e5e5e5e5e5e5",
    client_id: "c1",
    pipeline_id: "p1",
    source_document_id: null,
    source_knowledge_item_id: null,
    item_type: "company_name",
    content: "Acme Corp",
    evidence_text: "page 1",
    evidence_page: 1,
    confidence: 0.9,
    status: "pending" as const,
    actor_id: null,
    actor_note: null,
    edited_content: null,
    decided_at: null,
    created_at: NOW,
    updated_at: NOW,
  };

  it("parses valid review item", () => {
    const result = ReviewItemResponseSchema.parse(valid);
    expect(result.status).toBe("pending");
    expect(result.confidence).toBe(0.9);
  });

  it("accepts approved status", () => {
    const result = ReviewItemResponseSchema.parse({ ...valid, status: "approved" });
    expect(result.status).toBe("approved");
  });

  it("rejects missing id", () => {
    expect(() => ReviewItemResponseSchema.parse({ ...valid, id: "" })).toThrow();
  });
});

describe("ReviewDecisionSchema", () => {
  it("parses approve decision", () => {
    const result = ReviewDecisionSchema.parse({ status: "approved" });
    expect(result.status).toBe("approved");
  });

  it("parses edited_and_approved with content", () => {
    const result = ReviewDecisionSchema.parse({
      status: "edited_and_approved",
      edited_content: "Fixed Corp",
      actor_id: "user1",
    });
    expect(result.edited_content).toBe("Fixed Corp");
  });

  it("rejects invalid status", () => {
    expect(() => ReviewDecisionSchema.parse({ status: "maybe" })).toThrow();
  });
});

describe("ActiveICPConfigResponseSchema", () => {
  const valid = {
    id: "id1",
    client_id: "c1",
    pipeline_id: "p1",
    pipeline_config_version_id: null,
    vertical: "SaaS",
    target_company_size_min: null,
    target_company_size_max: null,
    geographies: ["US"],
    titles: ["CTO"],
    signals: ["hiring"],
    exclusions: [],
    notes: null,
    activated_by: "admin",
    activated_at: NOW,
    created_at: NOW,
    updated_at: NOW,
  };

  it("parses valid ICP config", () => {
    const result = ActiveICPConfigResponseSchema.parse(valid);
    expect(result.vertical).toBe("SaaS");
    expect(result.titles).toEqual(["CTO"]);
  });

  it("accepts null vertical", () => {
    const result = ActiveICPConfigResponseSchema.parse({ ...valid, vertical: null });
    expect(result.vertical).toBeNull();
  });
});

describe("ActiveICPConfigUpsertSchema", () => {
  it("applies list defaults", () => {
    const result = ActiveICPConfigUpsertSchema.parse({});
    expect(result.geographies).toEqual([]);
    expect(result.titles).toEqual([]);
  });

  it("parses full payload", () => {
    const result = ActiveICPConfigUpsertSchema.parse({
      vertical: "SaaS",
      titles: ["CTO"],
      geographies: ["US"],
      signals: ["hiring"],
      exclusions: [],
      activated_by: "admin",
    });
    expect(result.vertical).toBe("SaaS");
  });
});

describe("SuppressionRuleCreateSchema", () => {
  it("parses valid rule", () => {
    const result = SuppressionRuleCreateSchema.parse({ rule_type: "domain", value: "spam.com" });
    expect(result.rule_type).toBe("domain");
  });

  it("rejects invalid rule_type", () => {
    expect(() =>
      SuppressionRuleCreateSchema.parse({ rule_type: "unknown", value: "x" })
    ).toThrow();
  });

  it("rejects empty value", () => {
    expect(() =>
      SuppressionRuleCreateSchema.parse({ rule_type: "domain", value: "" })
    ).toThrow();
  });
});

describe("SuppressionRuleResponseSchema", () => {
  it("parses valid suppression rule", () => {
    const result = SuppressionRuleResponseSchema.parse({
      id: "id1",
      client_id: "c1",
      pipeline_id: "p1",
      rule_type: "domain",
      value: "spam.com",
      reason: null,
      added_by: null,
      created_at: NOW,
    });
    expect(result.value).toBe("spam.com");
  });
});

describe("EnrichmentGuardrailUpsertSchema", () => {
  it("parses valid upsert", () => {
    const result = EnrichmentGuardrailUpsertSchema.parse({
      guardrail_type: "enrichment_provider",
      enabled: true,
    });
    expect(result.enabled).toBe(true);
  });

  it("rejects invalid guardrail_type", () => {
    expect(() =>
      EnrichmentGuardrailUpsertSchema.parse({ guardrail_type: "unknown", enabled: true })
    ).toThrow();
  });
});

describe("EnrichmentGuardrailResponseSchema", () => {
  it("parses valid guardrail", () => {
    const result = EnrichmentGuardrailResponseSchema.parse({
      id: "id1",
      client_id: "c1",
      pipeline_id: "p1",
      guardrail_type: "enrichment_provider",
      enabled: true,
      policy_notes: null,
      approved_by: "admin",
      approved_at: NOW,
      created_at: NOW,
      updated_at: NOW,
    });
    expect(result.enabled).toBe(true);
  });
});

describe("ConfigAuditLogResponseSchema", () => {
  it("parses valid audit log entry", () => {
    const result = ConfigAuditLogResponseSchema.parse({
      id: "id1",
      client_id: "c1",
      pipeline_id: "p1",
      actor_id: "admin",
      action: "created",
      entity_type: "review_item",
      entity_id: "e1",
      before_snapshot: null,
      after_snapshot: '{"status":"pending"}',
      created_at: NOW,
    });
    expect(result.action).toBe("created");
  });
});
