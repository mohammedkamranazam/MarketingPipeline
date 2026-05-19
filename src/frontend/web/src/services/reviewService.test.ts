/**
 * Tests for reviewService.
 *
 * Acceptance criteria tested:
 * - listReviewItems fetches and validates review item list.
 * - listReviewItems with status filter appends ?status= query param.
 * - getReviewItem fetches single item by id.
 * - decideReviewItem POSTs decision and returns updated item.
 * - getICPConfig fetches and validates config; returns null on 404.
 * - upsertICPConfig PUTs config and returns updated config.
 * - listSuppressionRules fetches rule list.
 * - addSuppressionRule POSTs and returns new rule.
 * - deleteSuppressionRule sends DELETE request.
 * - listGuardrails fetches guardrail list.
 * - upsertGuardrail PUTs guardrail and returns result.
 * - listAuditLog fetches audit entries.
 */
import { afterEach, beforeAll, describe, expect, it } from "vitest";
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";
import {
  FIXTURE_GUARDRAIL,
  FIXTURE_ICP_CONFIG,
  FIXTURE_PIPELINE_A,
  FIXTURE_PIPELINE_B,
  FIXTURE_REVIEW_ITEM,
  FIXTURE_SUPPRESSION_RULE,
  handlers,
  FIXTURE_CLIENT,
} from "../test/msw/handlers";
import {
  addSuppressionRule,
  decideReviewItem,
  deleteSuppressionRule,
  getICPConfig,
  getReviewItem,
  listAuditLog,
  listGuardrails,
  listReviewItems,
  listSuppressionRules,
  upsertGuardrail,
  upsertICPConfig,
} from "./reviewService";

const server = setupServer(...handlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());

const CID = FIXTURE_CLIENT.id;
const PID = FIXTURE_PIPELINE_A.id;
const PID_B = FIXTURE_PIPELINE_B.id;

describe("listReviewItems", () => {
  it("fetches review item list", async () => {
    const items = await listReviewItems(CID, PID);
    expect(items).toHaveLength(1);
    expect(items.at(0)?.item_type).toBe("company_name");
  });

  it("appends status query param", async () => {
    let capturedUrl = "";
    server.use(
      http.get("http://localhost/clients/:cid/pipelines/:pid/review-items", ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json([FIXTURE_REVIEW_ITEM]);
      }),
    );
    await listReviewItems(CID, PID, "pending");
    expect(capturedUrl).toContain("status=pending");
  });
});

describe("getReviewItem", () => {
  it("fetches single review item", async () => {
    const item = await getReviewItem(CID, PID, FIXTURE_REVIEW_ITEM.id);
    expect(item.content).toBe("Acme Corp");
  });

  it("throws on 404", async () => {
    await expect(getReviewItem(CID, PID, "nonexistent-id")).rejects.toThrow();
  });
});

describe("decideReviewItem", () => {
  it("posts decision and returns updated item", async () => {
    const item = await decideReviewItem(CID, PID, FIXTURE_REVIEW_ITEM.id, {
      status: "approved",
    });
    expect(item.status).toBe("approved");
    expect(item.decided_at).toBeTruthy();
  });
});

describe("getICPConfig", () => {
  it("fetches config for pipeline with config", async () => {
    const config = await getICPConfig(CID, PID);
    expect(config).not.toBeNull();
    expect(config?.vertical).toBe("SaaS");
  });

  it("returns null for pipeline without config (404)", async () => {
    const config = await getICPConfig(CID, PID_B);
    expect(config).toBeNull();
  });
});

describe("upsertICPConfig", () => {
  it("PUTs config and returns result", async () => {
    const config = await upsertICPConfig(CID, PID, {
      vertical: "FinTech",
      titles: ["CFO"],
      geographies: [],
      signals: [],
      exclusions: [],
    });
    expect(config.vertical).toBe("FinTech");
  });
});

describe("listSuppressionRules", () => {
  it("fetches rule list", async () => {
    const rules = await listSuppressionRules(CID, PID);
    expect(rules).toHaveLength(1);
    expect(rules.at(0)?.value).toBe("spam.com");
  });
});

describe("addSuppressionRule", () => {
  it("posts new rule and returns it", async () => {
    const rule = await addSuppressionRule(CID, PID, {
      rule_type: "domain",
      value: "evil.com",
    });
    expect(rule.rule_type).toBe("domain");
  });
});

describe("deleteSuppressionRule", () => {
  it("sends DELETE request without error", async () => {
    await expect(
      deleteSuppressionRule(CID, PID, FIXTURE_SUPPRESSION_RULE.id)
    ).resolves.toBeUndefined();
  });

  it("throws on 404", async () => {
    await expect(
      deleteSuppressionRule(CID, PID, "unknown-id")
    ).rejects.toThrow();
  });
});

describe("listGuardrails", () => {
  it("fetches guardrail list", async () => {
    const guardrails = await listGuardrails(CID, PID);
    expect(guardrails).toHaveLength(1);
    expect(guardrails.at(0)?.guardrail_type).toBe("enrichment_provider");
  });
});

describe("upsertGuardrail", () => {
  it("PUTs guardrail and returns result", async () => {
    const g = await upsertGuardrail(CID, PID, {
      guardrail_type: "enrichment_provider",
      enabled: false,
    });
    expect(g.enabled).toBe(false);
  });
});

describe("listAuditLog", () => {
  it("fetches audit entries", async () => {
    const logs = await listAuditLog(CID, PID);
    expect(Array.isArray(logs)).toBe(true);
  });
});

describe("fixture types", () => {
  it("FIXTURE_GUARDRAIL has expected guardrail_type", () => {
    expect(FIXTURE_GUARDRAIL.guardrail_type).toBe("enrichment_provider");
  });

  it("FIXTURE_ICP_CONFIG has expected vertical", () => {
    expect(FIXTURE_ICP_CONFIG.vertical).toBe("SaaS");
  });
});
