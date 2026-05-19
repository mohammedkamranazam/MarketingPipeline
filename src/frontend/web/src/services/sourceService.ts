/**
 * Acceptance Criteria:
 * - listSourceConnectors(clientId, pipelineId, sourceType?) fetches GET /sources with optional filter.
 * - getSourceConnector(clientId, pipelineId, connectorId) fetches a single connector; returns null on 404.
 * - createSourceConnector(clientId, pipelineId, payload) POSTs to /sources.
 * - updateSourceConnector(clientId, pipelineId, connectorId, payload) PATCHes /sources/:id.
 * - deleteSourceConnector(clientId, pipelineId, connectorId) DELETEs /sources/:id.
 * - testSourceConnector(clientId, pipelineId, connectorId) POSTs to /sources/:id/test.
 * - listPolicyRules(clientId, pipelineId) fetches GET /policy-rules.
 * - createPolicyRule(clientId, pipelineId, payload) POSTs to /policy-rules.
 * - deletePolicyRule(clientId, pipelineId, ruleId) DELETEs /policy-rules/:id.
 * - decidePolicy(clientId, pipelineId, payload) POSTs to /policy/decide.
 * - listURLCandidates(clientId, pipelineId, status?) fetches GET /url-candidates with optional filter.
 * - submitURLCandidate(clientId, pipelineId, url) POSTs to /url-candidates.
 * - listCredentialProfiles(clientId, pipelineId) fetches GET /credentials.
 * - getCredentialProfile(clientId, pipelineId, profileId) fetches a single profile; returns null on 404.
 * - createCredentialProfile(clientId, pipelineId, payload) POSTs to /credentials.
 * - updateCredentialProfile(clientId, pipelineId, profileId, payload) PATCHes /credentials/:id.
 * - validateCredential(clientId, pipelineId, profileId) POSTs to /credentials/:id/validate.
 * - listAdapters() fetches GET /adapters.
 * - All responses validated with Zod schemas.
 * - No TypeScript `any`.
 */
import { ApiError, apiFetch } from "./apiClient";
import {
  AdapterRegistryListResponseSchema,
  CredentialProfileListResponseSchema,
  CredentialProfileResponseSchema,
  CredentialValidationRunResponseSchema,
  PolicyDecisionResponseSchema,
  PolicyRuleListResponseSchema,
  PolicyRuleResponseSchema,
  SourceConnectorListResponseSchema,
  SourceConnectorResponseSchema,
  SourceTestResultSchema,
  URLCandidateListResponseSchema,
  URLCandidateResponseSchema,
  type AdapterRegistryResponse,
  type CredentialProfileCreate,
  type CredentialProfileResponse,
  type CredentialProfileUpdate,
  type CredentialValidationRunResponse,
  type PolicyDecisionRequest,
  type PolicyDecisionResponse,
  type PolicyRuleCreate,
  type PolicyRuleResponse,
  type SourceConnectorCreate,
  type SourceConnectorResponse,
  type SourceConnectorUpdate,
  type SourceTestResult,
  type URLCandidateResponse,
} from "../contracts/source";

function base(clientId: string, pipelineId: string): string {
  return `/clients/${clientId}/pipelines/${pipelineId}`;
}

// ── SourceConnectors ──────────────────────────────────────────────────────────

export async function listSourceConnectors(
  clientId: string,
  pipelineId: string,
  sourceType?: string,
): Promise<SourceConnectorResponse[]> {
  const params = sourceType ? `?source_type=${encodeURIComponent(sourceType)}` : "";
  const data = await apiFetch(`${base(clientId, pipelineId)}/sources${params}`);
  return SourceConnectorListResponseSchema.parse(data);
}

export async function getSourceConnector(
  clientId: string,
  pipelineId: string,
  connectorId: string,
): Promise<SourceConnectorResponse | null> {
  try {
    const data = await apiFetch(`${base(clientId, pipelineId)}/sources/${connectorId}`);
    return SourceConnectorResponseSchema.parse(data);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function createSourceConnector(
  clientId: string,
  pipelineId: string,
  payload: SourceConnectorCreate,
): Promise<SourceConnectorResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return SourceConnectorResponseSchema.parse(data);
}

export async function updateSourceConnector(
  clientId: string,
  pipelineId: string,
  connectorId: string,
  payload: SourceConnectorUpdate,
): Promise<SourceConnectorResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/sources/${connectorId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return SourceConnectorResponseSchema.parse(data);
}

export async function deleteSourceConnector(
  clientId: string,
  pipelineId: string,
  connectorId: string,
): Promise<void> {
  await apiFetch(`${base(clientId, pipelineId)}/sources/${connectorId}`, {
    method: "DELETE",
  });
}

export async function testSourceConnector(
  clientId: string,
  pipelineId: string,
  connectorId: string,
): Promise<SourceTestResult> {
  const data = await apiFetch(
    `${base(clientId, pipelineId)}/sources/${connectorId}/test`,
    { method: "POST" },
  );
  return SourceTestResultSchema.parse(data);
}

// ── PolicyRules ───────────────────────────────────────────────────────────────

export async function listPolicyRules(
  clientId: string,
  pipelineId: string,
): Promise<PolicyRuleResponse[]> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/policy-rules`);
  return PolicyRuleListResponseSchema.parse(data);
}

export async function createPolicyRule(
  clientId: string,
  pipelineId: string,
  payload: PolicyRuleCreate,
): Promise<PolicyRuleResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/policy-rules`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return PolicyRuleResponseSchema.parse(data);
}

export async function deletePolicyRule(
  clientId: string,
  pipelineId: string,
  ruleId: string,
): Promise<void> {
  await apiFetch(`${base(clientId, pipelineId)}/policy-rules/${ruleId}`, {
    method: "DELETE",
  });
}

export async function decidePolicy(
  clientId: string,
  pipelineId: string,
  payload: PolicyDecisionRequest,
): Promise<PolicyDecisionResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/policy/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return PolicyDecisionResponseSchema.parse(data);
}

// ── URLCandidates ─────────────────────────────────────────────────────────────

export async function listURLCandidates(
  clientId: string,
  pipelineId: string,
  status?: string,
): Promise<URLCandidateResponse[]> {
  const params = status ? `?status=${encodeURIComponent(status)}` : "";
  const data = await apiFetch(`${base(clientId, pipelineId)}/url-candidates${params}`);
  return URLCandidateListResponseSchema.parse(data);
}

export async function submitURLCandidate(
  clientId: string,
  pipelineId: string,
  url: string,
): Promise<URLCandidateResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/url-candidates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return URLCandidateResponseSchema.parse(data);
}

// ── CredentialProfiles ────────────────────────────────────────────────────────

export async function listCredentialProfiles(
  clientId: string,
  pipelineId: string,
): Promise<CredentialProfileResponse[]> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/credentials`);
  return CredentialProfileListResponseSchema.parse(data);
}

export async function getCredentialProfile(
  clientId: string,
  pipelineId: string,
  profileId: string,
): Promise<CredentialProfileResponse | null> {
  try {
    const data = await apiFetch(`${base(clientId, pipelineId)}/credentials/${profileId}`);
    return CredentialProfileResponseSchema.parse(data);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null;
    throw err;
  }
}

export async function createCredentialProfile(
  clientId: string,
  pipelineId: string,
  payload: CredentialProfileCreate,
): Promise<CredentialProfileResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/credentials`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return CredentialProfileResponseSchema.parse(data);
}

export async function updateCredentialProfile(
  clientId: string,
  pipelineId: string,
  profileId: string,
  payload: CredentialProfileUpdate,
): Promise<CredentialProfileResponse> {
  const data = await apiFetch(`${base(clientId, pipelineId)}/credentials/${profileId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return CredentialProfileResponseSchema.parse(data);
}

export async function validateCredential(
  clientId: string,
  pipelineId: string,
  profileId: string,
): Promise<CredentialValidationRunResponse> {
  const data = await apiFetch(
    `${base(clientId, pipelineId)}/credentials/${profileId}/validate`,
    { method: "POST" },
  );
  return CredentialValidationRunResponseSchema.parse(data);
}

// ── AdapterRegistry ───────────────────────────────────────────────────────────

export async function listAdapters(): Promise<AdapterRegistryResponse[]> {
  const data = await apiFetch("/adapters");
  return AdapterRegistryListResponseSchema.parse(data);
}
