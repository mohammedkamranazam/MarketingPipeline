"""
Acceptance Criteria:
- ReviewItemResponse exposes all ReviewItem fields with typed lists parsed from JSON.
- ReviewDecision carries status (approved | rejected | edited_and_approved),
  actor_id, actor_note, and edited_content (required when status is edited_and_approved).
- ActiveICPConfigResponse exposes all ActiveICPConfig fields; JSON text lists are
  returned as list[str].
- ActiveICPConfigUpsert is the write contract for creating/replacing an active config;
  titles, geographies, signals, exclusions are list[str].
- SuppressionRuleCreate carries rule_type, value, reason, added_by.
- SuppressionRuleResponse exposes all fields.
- EnrichmentGuardrailUpsert carries guardrail_type, enabled, policy_notes, approved_by.
- EnrichmentGuardrailResponse exposes all fields.
- ConfigAuditLogResponse exposes all audit fields.
- ReviewItemCreate allows creating a review item from any source (used in tests and
  seed scripts); evidence_text must be non-empty.
- No untyped dicts as contract fields.
"""

import json
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ReviewStatus = Literal["pending", "approved", "rejected", "edited_and_approved"]
RuleType = Literal["domain", "email", "company", "title"]
GuardrailType = Literal["enrichment_provider", "email_verification", "outreach_export"]


class ReviewItemCreate(BaseModel):
    item_type: str = Field(min_length=1)
    content: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    evidence_page: int | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    source_document_id: uuid.UUID | None = None
    source_knowledge_item_id: uuid.UUID | None = None


class ReviewItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    source_document_id: uuid.UUID | None
    source_knowledge_item_id: uuid.UUID | None
    item_type: str
    content: str
    evidence_text: str
    evidence_page: int | None
    confidence: float
    status: str
    actor_id: str | None
    actor_note: str | None
    edited_content: str | None
    decided_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ReviewDecision(BaseModel):
    status: ReviewStatus
    actor_id: str | None = None
    actor_note: str | None = None
    edited_content: str | None = None

    @model_validator(mode="after")
    def edited_content_required_when_edited(self) -> "ReviewDecision":
        if self.status == "edited_and_approved" and not self.edited_content:
            raise ValueError("edited_content is required when status is edited_and_approved")
        return self


class ActiveICPConfigUpsert(BaseModel):
    vertical: str | None = None
    target_company_size_min: int | None = None
    target_company_size_max: int | None = None
    geographies: list[str] = Field(default_factory=list)
    titles: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    notes: str | None = None
    activated_by: str | None = None
    pipeline_config_version_id: uuid.UUID | None = None


class ActiveICPConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    pipeline_config_version_id: uuid.UUID | None
    vertical: str | None
    target_company_size_min: int | None
    target_company_size_max: int | None
    geographies: list[str]
    titles: list[str]
    signals: list[str]
    exclusions: list[str]
    notes: str | None
    activated_by: str | None
    activated_at: datetime
    created_at: datetime
    updated_at: datetime

    @field_validator("geographies", "titles", "signals", "exclusions", mode="before")
    @classmethod
    def parse_json_list(cls, v: object) -> list[str]:
        if isinstance(v, str):
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        if isinstance(v, list):
            return v
        return []


class SuppressionRuleCreate(BaseModel):
    rule_type: RuleType
    value: str = Field(min_length=1)
    reason: str | None = None
    added_by: str | None = None


class SuppressionRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    rule_type: str
    value: str
    reason: str | None
    added_by: str | None
    created_at: datetime


class EnrichmentGuardrailUpsert(BaseModel):
    guardrail_type: GuardrailType
    enabled: bool
    policy_notes: str | None = None
    approved_by: str | None = None


class EnrichmentGuardrailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    guardrail_type: str
    enabled: bool
    policy_notes: str | None
    approved_by: str | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ConfigAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    actor_id: str | None
    action: str
    entity_type: str
    entity_id: uuid.UUID | None
    before_snapshot: str | None
    after_snapshot: str | None
    created_at: datetime
