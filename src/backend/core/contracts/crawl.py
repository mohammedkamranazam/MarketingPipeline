"""
Acceptance Criteria:
- CrawlJobCreate requires pipeline_id (inferred from route), source_connector_id (optional),
  job_type, trigger, max_attempts, rate_limit_per_minute (optional),
  robots_txt_url (optional), concurrency_budget (optional).
- CrawlJobResponse exposes all CrawlJob fields.
- CrawlJobUpdate allows updating status, error_code, error_message, trace_id.
- CrawlArtifactResponse exposes all CrawlArtifact fields.
- CrawlBudgetCreate requires client_id, pipeline_id (optional), source_connector_id (optional),
  adapter_key (optional), budget_type, max_concurrent.
- CrawlBudgetResponse exposes all CrawlBudget fields.
- ArtifactStoreRequest carries url, content, mime_type, artifact_type, policy_decision,
  crawl_job_id (optional), source_connector_id (optional), seed_lead_row_id (optional).
- RobotsCheckResult carries url, allowed (bool), reason (optional).
- No TypeScript `any`.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

ArtifactType = Literal[
    "html_page", "search_result", "profile_evidence",
    "provider_response", "import_artifact",
]

CrawlJobStatus = Literal[
    "queued", "running", "paused", "failed", "retrying",
    "completed", "blocked", "stale", "cancelled",
]


class CrawlJobCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source_connector_id: uuid.UUID | None = None
    job_type: str = "crawl"
    trigger: str = "api"
    max_attempts: int = 3
    rate_limit_per_minute: int | None = None
    robots_txt_url: str | None = None
    concurrency_budget: int | None = None


class CrawlJobUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: CrawlJobStatus | None = None
    error_code: str | None = None
    error_message: str | None = None
    trace_id: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class CrawlJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    source_connector_id: uuid.UUID | None
    job_type: str
    status: str
    idempotency_key: str
    trigger: str
    attempt: int
    max_attempts: int
    lease_owner: str | None
    lease_expires_at: datetime | None
    heartbeat_at: datetime | None
    scheduled_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    error_message: str | None
    trace_id: str | None
    rate_limit_per_minute: int | None
    robots_txt_url: str | None
    concurrency_budget: int | None
    created_at: datetime
    updated_at: datetime


class CrawlArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    crawl_job_id: uuid.UUID | None
    source_connector_id: uuid.UUID | None
    seed_lead_row_id: uuid.UUID | None
    artifact_type: str
    url: str | None
    storage_key: str
    content_hash: str | None
    status: str
    policy_decision: str | None
    mime_type: str | None
    size_bytes: int | None
    raw_metadata_json: str | None
    created_at: datetime
    updated_at: datetime


class CrawlBudgetCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pipeline_id: uuid.UUID | None = None
    source_connector_id: uuid.UUID | None = None
    adapter_key: str | None = None
    budget_type: str
    max_concurrent: int = 1


class CrawlBudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID | None
    source_connector_id: uuid.UUID | None
    adapter_key: str | None
    budget_type: str
    max_concurrent: int
    current_count: int
    created_at: datetime
    updated_at: datetime


class ArtifactStoreRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str | None = None
    content: str
    mime_type: str = "text/html"
    artifact_type: ArtifactType = "html_page"
    policy_decision: str | None = None
    crawl_job_id: uuid.UUID | None = None
    source_connector_id: uuid.UUID | None = None
    seed_lead_row_id: uuid.UUID | None = None


class RobotsCheckResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str
    allowed: bool
    reason: str | None = None
