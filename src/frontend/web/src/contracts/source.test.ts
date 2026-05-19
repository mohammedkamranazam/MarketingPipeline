/**
 * Contract schema tests for source.ts
 */
import { describe, expect, it } from "vitest";
import {
  AdapterRegistryResponseSchema,
  CredentialProfileResponseSchema,
  CredentialValidationRunResponseSchema,
  PolicyDecisionResponseSchema,
  PolicyRuleResponseSchema,
  SourceConnectorResponseSchema,
  SourceTestResultSchema,
  URLCandidateResponseSchema,
} from "./source";

const NOW = new Date().toISOString();

const BASE_CONNECTOR = {
  id: "c1",
  client_id: "cl1",
  pipeline_id: "p1",
  source_type: "public_web" as const,
  name: "My Source",
  base_url: null,
  adapter_key: "mock_search",
  status: "active" as const,
  config_json: null,
  rate_limit_per_minute: null,
  credential_profile_id: null,
  created_at: NOW,
  updated_at: NOW,
};

describe("SourceConnectorResponseSchema", () => {
  it("accepts valid connector", () => {
    expect(() => SourceConnectorResponseSchema.parse(BASE_CONNECTOR)).not.toThrow();
  });
  it("rejects invalid source_type", () => {
    expect(() =>
      SourceConnectorResponseSchema.parse({ ...BASE_CONNECTOR, source_type: "unknown" })
    ).toThrow();
  });
});

describe("SourceTestResultSchema", () => {
  it("accepts success result", () => {
    expect(() =>
      SourceTestResultSchema.parse({ adapter_key: "mock_search", success: true, latency_ms: 42, error: null })
    ).not.toThrow();
  });
  it("accepts failure result", () => {
    expect(() =>
      SourceTestResultSchema.parse({ adapter_key: "mock_search", success: false, latency_ms: null, error: "Uncertified" })
    ).not.toThrow();
  });
});

describe("PolicyRuleResponseSchema", () => {
  it("accepts valid rule", () => {
    expect(() =>
      PolicyRuleResponseSchema.parse({
        id: "r1", client_id: "cl1", pipeline_id: "p1",
        entity_type: "url_pattern", entity_id: null, pattern: "https://x.com",
        decision: "allow", priority: 100, reason: null,
        created_at: NOW, updated_at: NOW,
      })
    ).not.toThrow();
  });
  it("rejects invalid decision", () => {
    expect(() =>
      PolicyRuleResponseSchema.parse({
        id: "r1", client_id: "cl1", pipeline_id: "p1",
        entity_type: "url_pattern", entity_id: null, pattern: null,
        decision: "permit", priority: 100, reason: null,
        created_at: NOW, updated_at: NOW,
      })
    ).toThrow();
  });
});

describe("PolicyDecisionResponseSchema", () => {
  it("accepts allow decision", () => {
    expect(() =>
      PolicyDecisionResponseSchema.parse({ decision: "allow", matched_rule_id: "r1", reason: null })
    ).not.toThrow();
  });
  it("accepts review with null rule", () => {
    expect(() =>
      PolicyDecisionResponseSchema.parse({ decision: "review", matched_rule_id: null, reason: null })
    ).not.toThrow();
  });
});

describe("URLCandidateResponseSchema", () => {
  it("accepts valid candidate", () => {
    expect(() =>
      URLCandidateResponseSchema.parse({
        id: "u1", client_id: "cl1", pipeline_id: "p1",
        url: "https://ex.com", status: "allow", policy_decision: "allow",
        submitted_at: NOW, reviewed_at: null, reviewer_id: null,
      })
    ).not.toThrow();
  });
});

describe("CredentialProfileResponseSchema", () => {
  it("accepts valid profile", () => {
    expect(() =>
      CredentialProfileResponseSchema.parse({
        id: "cp1", client_id: "cl1", pipeline_id: "p1",
        name: "My Cred", adapter_key: "mock_search", status: "active",
        scopes: ["read"], masked_fingerprint: null,
        expires_at: null, last_validated_at: null,
        next_validation_at: null, rotation_due_at: null,
        created_at: NOW, updated_at: NOW,
      })
    ).not.toThrow();
  });
  it("rejects invalid status", () => {
    expect(() =>
      CredentialProfileResponseSchema.parse({
        id: "cp1", client_id: "cl1", pipeline_id: "p1",
        name: "My Cred", adapter_key: "mock_search", status: "ok",
        scopes: [], masked_fingerprint: null, expires_at: null,
        last_validated_at: null, next_validation_at: null, rotation_due_at: null,
        created_at: NOW, updated_at: NOW,
      })
    ).toThrow();
  });
});

describe("CredentialValidationRunResponseSchema", () => {
  it("accepts passed run", () => {
    expect(() =>
      CredentialValidationRunResponseSchema.parse({
        id: "vr1", credential_profile_id: "cp1",
        status: "passed", reason: null, ran_at: NOW,
      })
    ).not.toThrow();
  });
  it("accepts failed run with reason", () => {
    expect(() =>
      CredentialValidationRunResponseSchema.parse({
        id: "vr2", credential_profile_id: "cp1",
        status: "failed", reason: "Expired", ran_at: NOW,
      })
    ).not.toThrow();
  });
});

describe("AdapterRegistryResponseSchema", () => {
  it("accepts valid adapter", () => {
    expect(() =>
      AdapterRegistryResponseSchema.parse({
        id: "a1", adapter_key: "mock_search", display_name: "Mock",
        source_type: "search_provider", audit_event_type: "search.mock",
        timeout_seconds: 30, retry_class: "fast",
        terms_url: null, cost_model: null, is_certified: true,
        created_at: NOW, updated_at: NOW,
      })
    ).not.toThrow();
  });
});
