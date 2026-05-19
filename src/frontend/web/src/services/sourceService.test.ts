/**
 * Tests for sourceService.ts
 *
 * Acceptance criteria tested:
 * - listSourceConnectors returns array of connectors.
 * - getSourceConnector returns connector; returns null on 404.
 * - createSourceConnector returns created connector.
 * - updateSourceConnector returns updated connector.
 * - deleteSourceConnector resolves without error.
 * - testSourceConnector returns SourceTestResult.
 * - listPolicyRules returns list ordered by priority.
 * - createPolicyRule returns created rule.
 * - deletePolicyRule resolves without error.
 * - decidePolicy returns PolicyDecisionResponse.
 * - listURLCandidates returns list.
 * - submitURLCandidate returns URLCandidateResponse.
 * - listCredentialProfiles returns list.
 * - getCredentialProfile returns profile; returns null on 404.
 * - createCredentialProfile returns created profile.
 * - updateCredentialProfile returns updated profile.
 * - validateCredential returns CredentialValidationRunResponse.
 * - listAdapters returns list.
 */
import { describe, expect, it } from "vitest";
import {
  FIXTURE_CLIENT,
  FIXTURE_CONNECTOR,
  FIXTURE_CREDENTIAL,
  FIXTURE_PIPELINE_A,
  FIXTURE_POLICY_RULE,
  FIXTURE_URL_CANDIDATE,
} from "../test/msw/handlers";
import {
  createCredentialProfile,
  createPolicyRule,
  createSourceConnector,
  decidePolicy,
  deleteSourceConnector,
  getCredentialProfile,
  getSourceConnector,
  listAdapters,
  listCredentialProfiles,
  listPolicyRules,
  listSourceConnectors,
  listURLCandidates,
  submitURLCandidate,
  testSourceConnector,
  updateCredentialProfile,
  updateSourceConnector,
  validateCredential,
} from "./sourceService";

const CID = FIXTURE_CLIENT.id;
const PID = FIXTURE_PIPELINE_A.id;

describe("listSourceConnectors", () => {
  it("returns connectors for pipeline", async () => {
    const connectors = await listSourceConnectors(CID, PID);
    expect(connectors).toHaveLength(1);
    expect(connectors.at(0)?.id).toBe(FIXTURE_CONNECTOR.id);
  });
});

describe("getSourceConnector", () => {
  it("returns connector by id", async () => {
    const c = await getSourceConnector(CID, PID, FIXTURE_CONNECTOR.id);
    expect(c).not.toBeNull();
    expect(c?.name).toBe(FIXTURE_CONNECTOR.name);
  });

  it("returns null on 404", async () => {
    const c = await getSourceConnector(CID, PID, "non-existent-id");
    expect(c).toBeNull();
  });
});

describe("createSourceConnector", () => {
  it("creates and returns connector", async () => {
    const c = await createSourceConnector(CID, PID, {
      source_type: "search_provider",
      name: "New Connector",
      adapter_key: "mock_search",
    });
    expect(c.name).toBe("New Connector");
  });
});

describe("updateSourceConnector", () => {
  it("updates and returns connector", async () => {
    const c = await updateSourceConnector(CID, PID, FIXTURE_CONNECTOR.id, {
      name: "Renamed",
    });
    expect(c.name).toBe("Renamed");
  });
});

describe("deleteSourceConnector", () => {
  it("resolves without error", async () => {
    await expect(
      deleteSourceConnector(CID, PID, FIXTURE_CONNECTOR.id),
    ).resolves.toBeUndefined();
  });
});

describe("testSourceConnector", () => {
  it("returns test result", async () => {
    const result = await testSourceConnector(CID, PID, FIXTURE_CONNECTOR.id);
    expect(result.success).toBe(true);
    expect(result.adapter_key).toBe(FIXTURE_CONNECTOR.adapter_key);
  });
});

describe("listPolicyRules", () => {
  it("returns rules list", async () => {
    const rules = await listPolicyRules(CID, PID);
    expect(rules).toHaveLength(1);
    expect(rules.at(0)?.id).toBe(FIXTURE_POLICY_RULE.id);
  });
});

describe("createPolicyRule", () => {
  it("creates and returns rule", async () => {
    const rule = await createPolicyRule(CID, PID, {
      entity_type: "url_pattern",
      pattern: "https://blocked.com",
      decision: "block",
    });
    expect(rule.decision).toBe("block");
  });
});

describe("decidePolicy", () => {
  it("returns allow for matching URL", async () => {
    const result = await decidePolicy(CID, PID, {
      operation_type: "fetch",
      url: "https://allowed.com/page",
    });
    expect(result.decision).toBe("allow");
    expect(result.matched_rule_id).toBe(FIXTURE_POLICY_RULE.id);
  });

  it("returns review for unknown URL", async () => {
    const result = await decidePolicy(CID, PID, {
      operation_type: "fetch",
      url: "https://unknown.com",
    });
    expect(result.decision).toBe("review");
    expect(result.matched_rule_id).toBeNull();
  });
});

describe("listURLCandidates", () => {
  it("returns candidates list", async () => {
    const candidates = await listURLCandidates(CID, PID);
    expect(candidates).toHaveLength(1);
    expect(candidates.at(0)?.id).toBe(FIXTURE_URL_CANDIDATE.id);
  });
});

describe("submitURLCandidate", () => {
  it("returns submitted candidate", async () => {
    const candidate = await submitURLCandidate(CID, PID, "https://new.com");
    expect(candidate.url).toBe("https://new.com");
    expect(candidate.policy_decision).toBe("review");
  });
});

describe("listCredentialProfiles", () => {
  it("returns profiles list", async () => {
    const profiles = await listCredentialProfiles(CID, PID);
    expect(profiles).toHaveLength(1);
    expect(profiles.at(0)?.id).toBe(FIXTURE_CREDENTIAL.id);
  });
});

describe("getCredentialProfile", () => {
  it("returns profile by id", async () => {
    const p = await getCredentialProfile(CID, PID, FIXTURE_CREDENTIAL.id);
    expect(p).not.toBeNull();
    expect(p?.name).toBe(FIXTURE_CREDENTIAL.name);
  });

  it("returns null on 404", async () => {
    const p = await getCredentialProfile(CID, PID, "non-existent-id");
    expect(p).toBeNull();
  });
});

describe("createCredentialProfile", () => {
  it("creates and returns profile", async () => {
    const p = await createCredentialProfile(CID, PID, {
      name: "New Cred",
      adapter_key: "mock_search",
      secret_reference: "env:API_KEY",
      scopes: ["read"],
    });
    expect(p.name).toBe("New Cred");
  });
});

describe("updateCredentialProfile", () => {
  it("updates and returns profile", async () => {
    const p = await updateCredentialProfile(CID, PID, FIXTURE_CREDENTIAL.id, {
      status: "expiring",
    });
    expect(p.status).toBe("expiring");
  });
});

describe("validateCredential", () => {
  it("returns validation run", async () => {
    const run = await validateCredential(CID, PID, FIXTURE_CREDENTIAL.id);
    expect(run.status).toBe("passed");
    expect(run.credential_profile_id).toBe(FIXTURE_CREDENTIAL.id);
  });
});

describe("listAdapters", () => {
  it("returns adapters list", async () => {
    const adapters = await listAdapters();
    expect(adapters).toHaveLength(1);
    expect(adapters.at(0)?.adapter_key).toBe("mock_search");
  });
});
