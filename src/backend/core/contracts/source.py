"""
Acceptance Criteria:
- SourceConnectorCreate carries source_type, name, base_url, adapter_key,
  rate_limit_per_minute, config_json, credential_profile_id.
- SourceConnectorResponse exposes all fields.
- SourceConnectorUpdate allows partial edits (status, name, base_url, rate_limit, config_json,
  credential_profile_id).
- PolicyRuleCreate carries entity_type, entity_id, pattern, decision, priority, reason.
- PolicyDecisionRequest carries operation_type and context dict (url or entity_id).
- PolicyDecisionResponse carries decision (allow|block|review), matched_rule_id, reason.
- URLCandidateCreate carries url, source_connector_id.
- URLCandidateResponse exposes all fields.
- CredentialProfileCreate carries name, adapter_key, secret_reference, scopes,
  expires_at, masked_fingerprint.
- CredentialProfileResponse exposes all fields except raw secret_reference value.
- CredentialValidationRunResponse exposes all fields.
- AdapterRegistryResponse exposes all fields.
- SourceTestResult carries adapter_key, success, latency_ms, error.
- No untyped dicts as contract fields.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal[
    "public_web", "search_provider", "enrichment_provider",
    "email_verification", "outreach_export",
]
PolicyDecision = Literal["allow", "block", "review"]
CredentialStatus = Literal[
    "active", "expiring", "expired", "validation_failed",
    "insufficient_scope", "revoked", "disabled",
]


# ── SourceConnector ───────────────────────────────────────────────────────────

class SourceConnectorCreate(BaseModel):
    source_type: SourceType
    name: str = Field(min_length=1)
    base_url: str | None = None
    adapter_key: str = Field(min_length=1)
    rate_limit_per_minute: int | None = Field(default=None, ge=1)
    config_json: str | None = None
    credential_profile_id: uuid.UUID | None = None


class SourceConnectorUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    status: str | None = None
    rate_limit_per_minute: int | None = None
    config_json: str | None = None
    credential_profile_id: uuid.UUID | None = None


class SourceConnectorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    source_type: str
    name: str
    base_url: str | None
    adapter_key: str
    status: str
    config_json: str | None
    rate_limit_per_minute: int | None
    credential_profile_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# ── PolicyRule ────────────────────────────────────────────────────────────────

class PolicyRuleCreate(BaseModel):
    entity_type: str = Field(min_length=1)
    entity_id: uuid.UUID | None = None
    pattern: str | None = None
    decision: PolicyDecision
    priority: int = Field(default=100, ge=1)
    reason: str | None = None


class PolicyRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID | None
    pattern: str | None
    decision: str
    priority: int
    reason: str | None
    created_at: datetime
    updated_at: datetime


class PolicyDecisionRequest(BaseModel):
    operation_type: str = Field(min_length=1)
    url: str | None = None
    entity_id: uuid.UUID | None = None
    source_connector_id: uuid.UUID | None = None


class PolicyDecisionResponse(BaseModel):
    decision: PolicyDecision
    matched_rule_id: uuid.UUID | None
    reason: str


# ── URLCandidate ──────────────────────────────────────────────────────────────

class URLCandidateCreate(BaseModel):
    url: str = Field(min_length=1)
    source_connector_id: uuid.UUID | None = None


class URLCandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    source_connector_id: uuid.UUID | None
    url: str
    status: str
    policy_decision: str
    discovered_at: datetime
    created_at: datetime
    updated_at: datetime


# ── CredentialProfile ─────────────────────────────────────────────────────────

class CredentialProfileCreate(BaseModel):
    name: str = Field(min_length=1)
    adapter_key: str = Field(min_length=1)
    secret_reference: str = Field(min_length=1)
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    masked_fingerprint: str | None = None


class CredentialProfileUpdate(BaseModel):
    name: str | None = None
    status: CredentialStatus | None = None
    scopes: list[str] | None = None
    expires_at: datetime | None = None
    masked_fingerprint: str | None = None
    rotation_due_at: datetime | None = None


class CredentialProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    name: str
    adapter_key: str
    status: str
    secret_reference: str
    scopes: str
    expires_at: datetime | None
    last_validated_at: datetime | None
    next_validation_at: datetime | None
    rotation_due_at: datetime | None
    masked_fingerprint: str | None
    created_at: datetime
    updated_at: datetime


class CredentialValidationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    credential_profile_id: uuid.UUID
    status: str
    reason: str | None
    checked_scopes: str
    created_at: datetime


# ── AdapterRegistry ───────────────────────────────────────────────────────────

class AdapterRegistryCreate(BaseModel):
    adapter_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    source_type: SourceType
    terms_url: str | None = None
    cost_model: str | None = None
    timeout_seconds: int = Field(default=30, ge=1)
    retry_class: str = Field(default="standard")
    audit_event_type: str = Field(min_length=1)
    is_certified: bool = False


class AdapterRegistryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    adapter_key: str
    display_name: str
    source_type: str
    terms_url: str | None
    cost_model: str | None
    timeout_seconds: int
    retry_class: str
    audit_event_type: str
    is_certified: bool
    created_at: datetime
    updated_at: datetime


# ── Source test ───────────────────────────────────────────────────────────────

class SourceTestResult(BaseModel):
    adapter_key: str
    success: bool
    latency_ms: int | None = None
    error: str | None = None
