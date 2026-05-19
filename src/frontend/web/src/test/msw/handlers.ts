/**
 * MSW request handlers for Phase 01–05 API fixtures.
 * Uses absolute URLs so the node MSW server can intercept them in Vitest.
 * Covers success, empty, 404, 422, and 500 states.
 */
import { http, HttpResponse } from "msw";
import type { ClientResponse, PipelineResponse } from "../../contracts/clients";
import type {
  CrawlArtifactResponse,
  CrawlBudgetResponse,
  CrawlJobResponse,
  RobotsCheckResult,
} from "../../contracts/crawl";
import type {
  DocumentResponse,
  LeadImportBatchResponse,
  SeedLeadRowResponse,
} from "../../contracts/ingestion";
import type {
  ActiveICPConfigResponse,
  EnrichmentGuardrailResponse,
  ReviewItemResponse,
  SuppressionRuleResponse,
} from "../../contracts/review";
import type {
  AdapterRegistryResponse,
  CredentialProfileResponse,
  CredentialValidationRunResponse,
  PolicyDecisionResponse,
  PolicyRuleResponse,
  SourceConnectorResponse,
  SourceTestResult,
  URLCandidateResponse,
} from "../../contracts/source";

const BASE = "http://localhost";
const NOW = new Date().toISOString();

export const FIXTURE_CLIENT: ClientResponse = {
  id: "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5",
  name: "tec5USA",
  slug: "tec5usa",
  status: "active",
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_PIPELINE_A: PipelineResponse = {
  id: "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6",
  client_id: FIXTURE_CLIENT.id,
  name: "Discovery 2024",
  slug: "discovery-2024",
  lane: "discovery",
  status: "active",
  description: "Account discovery pipeline",
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_PIPELINE_B: PipelineResponse = {
  id: "c3d4e5f6-a7b8-4c9d-0e1f-a2b3c4d5e6f7",
  client_id: FIXTURE_CLIENT.id,
  name: "Seed Enrichment Q1",
  slug: "seed-enrichment-q1",
  lane: "seed_enrichment",
  status: "active",
  description: null,
  created_at: NOW,
  updated_at: NOW,
};

// ---------------------------------------------------------------------------
// Phase 02 fixtures
// ---------------------------------------------------------------------------

export const FIXTURE_DOCUMENT: DocumentResponse = {
  id: "d1e2f3a4-b5c6-4d7e-8f9a-b0c1d2e3f4a5",
  client_id: "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5",
  pipeline_id: "b2c3d4e5-f6a7-4b8c-9d0e-f1a2b3c4d5e6",
  filename: "questionnaire_d1e2f3a4.txt",
  original_name: "tec5USA_questionnaire.txt",
  mime_type: "text/plain",
  size_bytes: 4096,
  storage_key: "documents/b2c3d4e5/questionnaire_d1e2f3a4.txt",
  status: "parsed",
  error_message: null,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_BATCH: LeadImportBatchResponse = {
  id: "e2f3a4b5-c6d7-4e8f-9a0b-c1d2e3f4a5b6",
  client_id: "a1b2c3d4-e5f6-4a7b-8c9d-e0f1a2b3c4d5",
  pipeline_id: "c3d4e5f6-a7b8-4c9d-0e1f-a2b3c4d5e6f7",
  filename: "leads_e2f3a4b5.csv",
  original_name: "ai_leads_q1.csv",
  mime_type: "text/csv",
  size_bytes: 2048,
  storage_key: "lead_imports/c3d4e5/leads_e2f3a4b5.csv",
  status: "completed",
  total_rows: 3,
  valid_rows: 2,
  error_rows: 1,
  error_message: null,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_ROW: SeedLeadRowResponse = {
  id: "f3a4b5c6-d7e8-4f9a-0b1c-d2e3f4a5b6c7",
  batch_id: FIXTURE_BATCH.id,
  client_id: FIXTURE_BATCH.client_id,
  pipeline_id: FIXTURE_BATCH.pipeline_id,
  row_index: 0,
  original_first_name: "alice",
  original_last_name: null,
  original_company: "acme corp",
  original_source: "LinkedIn",
  original_notes: "Q1 project",
  raw_values: '{"first_name":"alice","company":"acme corp"}',
  normalized_first_name: "Alice",
  normalized_last_name: null,
  normalized_company: "Acme Corp",
  normalized_source: "LinkedIn",
  status: "valid",
  validation_errors: [],
  is_duplicate: false,
  created_at: NOW,
};

// ---------------------------------------------------------------------------
// Phase 03 fixtures
// ---------------------------------------------------------------------------

export const FIXTURE_REVIEW_ITEM: ReviewItemResponse = {
  id: "a1a1a1a1-b2b2-4c3c-d4d4-e5e5e5e5e5e5",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  source_document_id: null,
  source_knowledge_item_id: null,
  item_type: "company_name",
  content: "Acme Corp",
  evidence_text: "Found on page 1 of the questionnaire",
  evidence_page: 1,
  confidence: 0.92,
  status: "pending",
  actor_id: null,
  actor_note: null,
  edited_content: null,
  decided_at: null,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_ICP_CONFIG: ActiveICPConfigResponse = {
  id: "b2b2b2b2-c3c3-4d4d-e5e5-f6f6f6f6f6f6",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  pipeline_config_version_id: null,
  vertical: "SaaS",
  target_company_size_min: null,
  target_company_size_max: null,
  geographies: ["US", "EU"],
  titles: ["CTO", "VP Engineering"],
  signals: ["hiring"],
  exclusions: ["government"],
  notes: null,
  activated_by: "admin",
  activated_at: NOW,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_SUPPRESSION_RULE: SuppressionRuleResponse = {
  id: "c3c3c3c3-d4d4-4e5e-f6f6-a7a7a7a7a7a7",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  rule_type: "domain",
  value: "spam.com",
  reason: "known spam domain",
  added_by: "admin",
  created_at: NOW,
};

export const FIXTURE_GUARDRAIL: EnrichmentGuardrailResponse = {
  id: "d4d4d4d4-e5e5-4f6f-a7a7-b8b8b8b8b8b8",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  guardrail_type: "enrichment_provider",
  enabled: true,
  policy_notes: null,
  approved_by: "admin",
  approved_at: NOW,
  created_at: NOW,
  updated_at: NOW,
};

// ---------------------------------------------------------------------------
// Phase 04 fixtures
// ---------------------------------------------------------------------------

export const FIXTURE_ADAPTER: AdapterRegistryResponse = {
  id: "ad000001-0000-4000-8000-000000000001",
  adapter_key: "mock_search",
  display_name: "Mock Search Provider",
  source_type: "search_provider",
  audit_event_type: "search.mock.executed",
  timeout_seconds: 10,
  retry_class: "fast",
  terms_url: null,
  cost_model: null,
  is_certified: true,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_CONNECTOR: SourceConnectorResponse = {
  id: "sc000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  source_type: "search_provider",
  name: "Mock Search",
  base_url: null,
  adapter_key: "mock_search",
  status: "active",
  config_json: null,
  rate_limit_per_minute: null,
  credential_profile_id: null,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_POLICY_RULE: PolicyRuleResponse = {
  id: "pr000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  entity_type: "url_pattern",
  entity_id: null,
  pattern: "https://allowed.com",
  decision: "allow",
  priority: 100,
  reason: "Known good domain",
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_URL_CANDIDATE: URLCandidateResponse = {
  id: "uc000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  url: "https://allowed.com/page",
  status: "allow",
  policy_decision: "allow",
  submitted_at: NOW,
  reviewed_at: null,
  reviewer_id: null,
};

export const FIXTURE_CREDENTIAL: CredentialProfileResponse = {
  id: "cp000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  name: "Mock Search API Key",
  adapter_key: "mock_search",
  status: "active",
  scopes: ["read", "search"],
  masked_fingerprint: "****abc123",
  expires_at: null,
  last_validated_at: NOW,
  next_validation_at: NOW,
  rotation_due_at: null,
  created_at: NOW,
  updated_at: NOW,
};

// ---------------------------------------------------------------------------
// Phase 05 fixtures
// ---------------------------------------------------------------------------

export const FIXTURE_CRAWL_JOB: CrawlJobResponse = {
  id: "cj000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  source_connector_id: null,
  job_type: "crawl",
  status: "queued",
  idempotency_key: `crawl:${FIXTURE_PIPELINE_A.id}:abc123`,
  trigger: "api",
  attempt: 0,
  max_attempts: 3,
  lease_owner: null,
  lease_expires_at: null,
  heartbeat_at: null,
  scheduled_at: NOW,
  started_at: null,
  finished_at: null,
  error_code: null,
  error_message: null,
  trace_id: null,
  rate_limit_per_minute: null,
  robots_txt_url: null,
  concurrency_budget: null,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_ARTIFACT: CrawlArtifactResponse = {
  id: "ar000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  crawl_job_id: FIXTURE_CRAWL_JOB.id,
  source_connector_id: null,
  seed_lead_row_id: null,
  artifact_type: "html_page",
  url: "https://example.com/page",
  storage_key: `artifacts/${FIXTURE_PIPELINE_A.id}/html_page/ar000001-0000-4000-8000-000000000001`,
  content_hash: "deadbeefdeadbeef",
  status: "stored",
  policy_decision: "allow",
  mime_type: "text/html",
  size_bytes: 256,
  raw_metadata_json: null,
  created_at: NOW,
  updated_at: NOW,
};

export const FIXTURE_BUDGET: CrawlBudgetResponse = {
  id: "bg000001-0000-4000-8000-000000000001",
  client_id: FIXTURE_CLIENT.id,
  pipeline_id: FIXTURE_PIPELINE_A.id,
  source_connector_id: null,
  adapter_key: null,
  budget_type: "pipeline",
  max_concurrent: 2,
  current_count: 1,
  created_at: NOW,
  updated_at: NOW,
};

export const handlers = [
  // GET /clients
  http.get(`${BASE}/clients`, () => HttpResponse.json([FIXTURE_CLIENT])),

  // POST /clients
  http.post(`${BASE}/clients`, async ({ request }) => {
    const body = (await request.json()) as Partial<ClientResponse>;
    const created: ClientResponse = {
      ...FIXTURE_CLIENT,
      id: "d4e5f6a7-b8c9-4d0e-1f2a-b3c4d5e6f7a8",
      name: body.name ?? "New Client",
      slug: body.slug ?? "new-client",
      status: body.status ?? "active",
    };
    return HttpResponse.json(created, { status: 201 });
  }),

  // GET /clients/:id
  http.get(`${BASE}/clients/:id`, ({ params }) => {
    if (params["id"] === FIXTURE_CLIENT.id) return HttpResponse.json(FIXTURE_CLIENT);
    return HttpResponse.json({ detail: "Not found" }, { status: 404 });
  }),

  // PATCH /clients/:id
  http.patch(`${BASE}/clients/:id`, async ({ params, request }) => {
    if (params["id"] !== FIXTURE_CLIENT.id)
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    const body = (await request.json()) as Partial<ClientResponse>;
    return HttpResponse.json({ ...FIXTURE_CLIENT, ...body });
  }),

  // GET /clients/:clientId/pipelines
  http.get(`${BASE}/clients/:clientId/pipelines`, ({ params }) => {
    if (params["clientId"] === FIXTURE_CLIENT.id)
      return HttpResponse.json([FIXTURE_PIPELINE_A, FIXTURE_PIPELINE_B]);
    return HttpResponse.json({ detail: "Not found" }, { status: 404 });
  }),

  // POST /clients/:clientId/pipelines
  http.post(`${BASE}/clients/:clientId/pipelines`, async ({ params, request }) => {
    if (params["clientId"] !== FIXTURE_CLIENT.id)
      return HttpResponse.json({ detail: "Client not found" }, { status: 404 });
    const body = (await request.json()) as Partial<PipelineResponse>;
    const created: PipelineResponse = {
      ...FIXTURE_PIPELINE_A,
      id: "e5f6a7b8-c9d0-4e1f-2a3b-c4d5e6f7a8b9",
      client_id: FIXTURE_CLIENT.id,
      name: body.name ?? "New Pipeline",
      slug: body.slug ?? "new-pipeline",
      lane: body.lane ?? "discovery",
      description: body.description ?? null,
      status: "active",
    };
    return HttpResponse.json(created, { status: 201 });
  }),

  // GET /clients/:clientId/pipelines/:pipelineId
  http.get(`${BASE}/clients/:clientId/pipelines/:pipelineId`, ({ params }) => {
    if (params["pipelineId"] === FIXTURE_PIPELINE_A.id)
      return HttpResponse.json(FIXTURE_PIPELINE_A);
    if (params["pipelineId"] === FIXTURE_PIPELINE_B.id)
      return HttpResponse.json(FIXTURE_PIPELINE_B);
    return HttpResponse.json({ detail: "Not found" }, { status: 404 });
  }),

  // PATCH /clients/:clientId/pipelines/:pipelineId
  http.patch(
    `${BASE}/clients/:clientId/pipelines/:pipelineId`,
    async ({ params, request }) => {
      const base =
        params["pipelineId"] === FIXTURE_PIPELINE_A.id
          ? FIXTURE_PIPELINE_A
          : params["pipelineId"] === FIXTURE_PIPELINE_B.id
            ? FIXTURE_PIPELINE_B
            : null;
      if (!base) return HttpResponse.json({ detail: "Not found" }, { status: 404 });
      const body = (await request.json()) as Partial<PipelineResponse>;
      return HttpResponse.json({ ...base, ...body });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/documents
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/documents`,
    ({ params }) => {
      if (params["pipelineId"] === FIXTURE_PIPELINE_A.id)
        return HttpResponse.json([FIXTURE_DOCUMENT]);
      return HttpResponse.json([]);
    },
  ),

  // POST /clients/:cid/pipelines/:pid/documents (multipart)
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/documents`,
    () => HttpResponse.json(FIXTURE_DOCUMENT, { status: 201 }),
  ),

  // GET /clients/:cid/pipelines/:pid/documents/:docId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/documents/:documentId`,
    ({ params }) => {
      if (params["documentId"] === FIXTURE_DOCUMENT.id)
        return HttpResponse.json(FIXTURE_DOCUMENT);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/documents/:docId/knowledge
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/documents/:documentId/knowledge`,
    () => HttpResponse.json([]),
  ),

  // GET /clients/:cid/pipelines/:pid/lead-imports
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/lead-imports`,
    ({ params }) => {
      if (params["pipelineId"] === FIXTURE_PIPELINE_B.id)
        return HttpResponse.json([FIXTURE_BATCH]);
      return HttpResponse.json([]);
    },
  ),

  // POST /clients/:cid/pipelines/:pid/lead-imports (multipart)
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/lead-imports`,
    () => HttpResponse.json(FIXTURE_BATCH, { status: 201 }),
  ),

  // GET /clients/:cid/pipelines/:pid/lead-imports/:batchId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/lead-imports/:batchId`,
    ({ params }) => {
      if (params["batchId"] === FIXTURE_BATCH.id)
        return HttpResponse.json(FIXTURE_BATCH);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/lead-imports/:batchId/rows
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/lead-imports/:batchId/rows`,
    ({ params }) => {
      if (params["batchId"] === FIXTURE_BATCH.id)
        return HttpResponse.json([FIXTURE_ROW]);
      return HttpResponse.json([]);
    },
  ),

  // ---------------------------------------------------------------------------
  // Phase 03 handlers
  // ---------------------------------------------------------------------------

  // GET /clients/:cid/pipelines/:pid/review-items
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/review-items`,
    () => HttpResponse.json([FIXTURE_REVIEW_ITEM]),
  ),

  // POST /clients/:cid/pipelines/:pid/review-items
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/review-items`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<ReviewItemResponse>;
      return HttpResponse.json(
        { ...FIXTURE_REVIEW_ITEM, ...body, status: "pending" },
        { status: 201 },
      );
    },
  ),

  // GET /clients/:cid/pipelines/:pid/review-items/:itemId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/review-items/:itemId`,
    ({ params }) => {
      if (params["itemId"] === FIXTURE_REVIEW_ITEM.id)
        return HttpResponse.json(FIXTURE_REVIEW_ITEM);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/review-items/:itemId/decide
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/review-items/:itemId/decide`,
    async ({ params, request }) => {
      if (params["itemId"] !== FIXTURE_REVIEW_ITEM.id)
        return HttpResponse.json({ detail: "Not found" }, { status: 404 });
      const body = (await request.json()) as { status: string };
      return HttpResponse.json({
        ...FIXTURE_REVIEW_ITEM,
        status: body.status,
        decided_at: NOW,
      });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/icp-config
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/icp-config`,
    ({ params }) => {
      if (params["pipelineId"] === FIXTURE_PIPELINE_A.id)
        return HttpResponse.json(FIXTURE_ICP_CONFIG);
      return HttpResponse.json({ detail: "No active ICP config" }, { status: 404 });
    },
  ),

  // PUT /clients/:cid/pipelines/:pid/icp-config
  http.put(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/icp-config`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<ActiveICPConfigResponse>;
      return HttpResponse.json({ ...FIXTURE_ICP_CONFIG, ...body });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/suppression-rules
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/suppression-rules`,
    () => HttpResponse.json([FIXTURE_SUPPRESSION_RULE]),
  ),

  // POST /clients/:cid/pipelines/:pid/suppression-rules
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/suppression-rules`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<SuppressionRuleResponse>;
      return HttpResponse.json(
        { ...FIXTURE_SUPPRESSION_RULE, ...body },
        { status: 201 },
      );
    },
  ),

  // DELETE /clients/:cid/pipelines/:pid/suppression-rules/:ruleId
  http.delete(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/suppression-rules/:ruleId`,
    ({ params }) => {
      if (params["ruleId"] === FIXTURE_SUPPRESSION_RULE.id)
        return new HttpResponse(null, { status: 204 });
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/guardrails
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/guardrails`,
    () => HttpResponse.json([FIXTURE_GUARDRAIL]),
  ),

  // PUT /clients/:cid/pipelines/:pid/guardrails
  http.put(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/guardrails`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<EnrichmentGuardrailResponse>;
      return HttpResponse.json({ ...FIXTURE_GUARDRAIL, ...body });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/audit-log
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/audit-log`,
    () => HttpResponse.json([]),
  ),

  // ---------------------------------------------------------------------------
  // Phase 04 handlers
  // ---------------------------------------------------------------------------

  // GET /adapters
  http.get(`${BASE}/adapters`, () => HttpResponse.json([FIXTURE_ADAPTER])),

  // POST /adapters
  http.post(`${BASE}/adapters`, async ({ request }) => {
    const body = (await request.json()) as Partial<AdapterRegistryResponse>;
    return HttpResponse.json({ ...FIXTURE_ADAPTER, ...body }, { status: 201 });
  }),

  // GET /clients/:cid/pipelines/:pid/sources
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/sources`,
    () => HttpResponse.json([FIXTURE_CONNECTOR]),
  ),

  // POST /clients/:cid/pipelines/:pid/sources
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/sources`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<SourceConnectorResponse>;
      return HttpResponse.json({ ...FIXTURE_CONNECTOR, ...body }, { status: 201 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/sources/:connectorId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/sources/:connectorId`,
    ({ params }) => {
      if (params["connectorId"] === FIXTURE_CONNECTOR.id)
        return HttpResponse.json(FIXTURE_CONNECTOR);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // PATCH /clients/:cid/pipelines/:pid/sources/:connectorId
  http.patch(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/sources/:connectorId`,
    async ({ params, request }) => {
      if (params["connectorId"] !== FIXTURE_CONNECTOR.id)
        return HttpResponse.json({ detail: "Not found" }, { status: 422 });
      const body = (await request.json()) as Partial<SourceConnectorResponse>;
      return HttpResponse.json({ ...FIXTURE_CONNECTOR, ...body });
    },
  ),

  // DELETE /clients/:cid/pipelines/:pid/sources/:connectorId
  http.delete(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/sources/:connectorId`,
    ({ params }) => {
      if (params["connectorId"] === FIXTURE_CONNECTOR.id)
        return new HttpResponse(null, { status: 204 });
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/sources/:connectorId/test
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/sources/:connectorId/test`,
    ({ params }) => {
      const result: SourceTestResult = {
        adapter_key: FIXTURE_CONNECTOR.adapter_key,
        success: params["connectorId"] === FIXTURE_CONNECTOR.id,
        latency_ms: 42,
        error: null,
      };
      return HttpResponse.json(result);
    },
  ),

  // GET /clients/:cid/pipelines/:pid/policy-rules
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/policy-rules`,
    () => HttpResponse.json([FIXTURE_POLICY_RULE]),
  ),

  // POST /clients/:cid/pipelines/:pid/policy-rules
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/policy-rules`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<PolicyRuleResponse>;
      return HttpResponse.json({ ...FIXTURE_POLICY_RULE, ...body }, { status: 201 });
    },
  ),

  // DELETE /clients/:cid/pipelines/:pid/policy-rules/:ruleId
  http.delete(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/policy-rules/:ruleId`,
    ({ params }) => {
      if (params["ruleId"] === FIXTURE_POLICY_RULE.id)
        return new HttpResponse(null, { status: 204 });
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/policy/decide
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/policy/decide`,
    async ({ request }) => {
      const body = (await request.json()) as { url?: string };
      const decision: PolicyDecisionResponse = {
        decision: body.url?.startsWith("https://allowed.com") ? "allow" : "review",
        matched_rule_id: body.url?.startsWith("https://allowed.com")
          ? FIXTURE_POLICY_RULE.id
          : null,
        reason: null,
      };
      return HttpResponse.json(decision);
    },
  ),

  // GET /clients/:cid/pipelines/:pid/url-candidates
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/url-candidates`,
    () => HttpResponse.json([FIXTURE_URL_CANDIDATE]),
  ),

  // POST /clients/:cid/pipelines/:pid/url-candidates
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/url-candidates`,
    async ({ request }) => {
      const body = (await request.json()) as { url: string };
      const candidate: URLCandidateResponse = {
        ...FIXTURE_URL_CANDIDATE,
        url: body.url,
        policy_decision: "review",
      };
      return HttpResponse.json(candidate, { status: 201 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/credentials
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/credentials`,
    () => HttpResponse.json([FIXTURE_CREDENTIAL]),
  ),

  // POST /clients/:cid/pipelines/:pid/credentials
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/credentials`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<CredentialProfileResponse>;
      return HttpResponse.json({ ...FIXTURE_CREDENTIAL, ...body }, { status: 201 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/credentials/:profileId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/credentials/:profileId`,
    ({ params }) => {
      if (params["profileId"] === FIXTURE_CREDENTIAL.id)
        return HttpResponse.json(FIXTURE_CREDENTIAL);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // PATCH /clients/:cid/pipelines/:pid/credentials/:profileId
  http.patch(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/credentials/:profileId`,
    async ({ params, request }) => {
      if (params["profileId"] !== FIXTURE_CREDENTIAL.id)
        return HttpResponse.json({ detail: "Not found" }, { status: 422 });
      const body = (await request.json()) as Partial<CredentialProfileResponse>;
      return HttpResponse.json({ ...FIXTURE_CREDENTIAL, ...body });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/credentials/:profileId/validate
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/credentials/:profileId/validate`,
    ({ params }) => {
      if (params["profileId"] !== FIXTURE_CREDENTIAL.id)
        return HttpResponse.json({ detail: "Not found" }, { status: 404 });
      const run: CredentialValidationRunResponse = {
        id: "vr-00000001",
        credential_profile_id: FIXTURE_CREDENTIAL.id,
        status: "passed",
        reason: null,
        ran_at: NOW,
      };
      return HttpResponse.json(run);
    },
  ),

  // ---------------------------------------------------------------------------
  // Phase 05 handlers
  // ---------------------------------------------------------------------------

  // GET /clients/:cid/pipelines/:pid/crawl-jobs
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/crawl-jobs`,
    () => HttpResponse.json([FIXTURE_CRAWL_JOB]),
  ),

  // POST /clients/:cid/pipelines/:pid/crawl-jobs
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/crawl-jobs`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<CrawlJobResponse>;
      return HttpResponse.json({ ...FIXTURE_CRAWL_JOB, ...body }, { status: 201 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/crawl-jobs/:jobId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/crawl-jobs/:jobId`,
    ({ params }) => {
      if (params["jobId"] === FIXTURE_CRAWL_JOB.id)
        return HttpResponse.json(FIXTURE_CRAWL_JOB);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/crawl-jobs/:jobId/cancel
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/crawl-jobs/:jobId/cancel`,
    ({ params }) => {
      if (params["jobId"] === FIXTURE_CRAWL_JOB.id)
        return new HttpResponse(null, { status: 204 });
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/crawl-jobs/:jobId/run
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/crawl-jobs/:jobId/run`,
    ({ params }) => {
      if (params["jobId"] !== FIXTURE_CRAWL_JOB.id)
        return HttpResponse.json({ detail: "Not found" }, { status: 404 });
      return HttpResponse.json(FIXTURE_ARTIFACT, { status: 201 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/artifacts
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/artifacts`,
    () => HttpResponse.json([FIXTURE_ARTIFACT]),
  ),

  // POST /clients/:cid/pipelines/:pid/artifacts
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/artifacts`,
    async ({ request }) => {
      const body = (await request.json()) as Partial<CrawlArtifactResponse>;
      return HttpResponse.json({ ...FIXTURE_ARTIFACT, ...body }, { status: 201 });
    },
  ),

  // GET /clients/:cid/pipelines/:pid/artifacts/:artifactId
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/artifacts/:artifactId`,
    ({ params }) => {
      if (params["artifactId"] === FIXTURE_ARTIFACT.id)
        return HttpResponse.json(FIXTURE_ARTIFACT);
      return HttpResponse.json({ detail: "Not found" }, { status: 404 });
    },
  ),

  // POST /clients/:cid/pipelines/:pid/robots-check
  http.post(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/robots-check`,
    async ({ request }) => {
      const url = new URL(request.url);
      const target = url.searchParams.get("url") ?? "";
      const result: RobotsCheckResult = {
        url: target,
        allowed: !target.includes("/private"),
        reason: target.includes("/private") ? "Path disallowed by robots.txt" : null,
      };
      return HttpResponse.json(result);
    },
  ),

  // GET /clients/:cid/pipelines/:pid/budgets
  http.get(
    `${BASE}/clients/:clientId/pipelines/:pipelineId/budgets`,
    () => HttpResponse.json([FIXTURE_BUDGET]),
  ),
];
