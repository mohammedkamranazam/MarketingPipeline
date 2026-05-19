"""
Acceptance Criteria:
- PipelineRunResponse includes id, client_id, pipeline_id, pipeline_config_version_id,
  run_type, status, trigger, created_at, started_at, finished_at.
- JobRunResponse includes id, run_id, client_id, pipeline_id, job_type, queue, status,
  attempt, max_attempts, idempotency_key, dedupe_key, retry_class, priority,
  lease_owner, lease_expires_at, heartbeat_at, scheduled_at, started_at, finished_at,
  error_code, error_message, trace_id.
- EventEnvelope matches the canonical event contract from 04-data-api-events.md.
- No untyped dicts as contract fields.
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

JobStatus = Literal[
    "queued",
    "leased",
    "running",
    "retrying",
    "paused_auth",
    "policy_blocked",
    "rate_limited",
    "manual_review_required",
    "dead_lettered",
    "cancelled",
    "succeeded",
    "failed",
]

RetryClass = Literal[
    "transient",
    "policy_blocked",
    "auth_required",
    "provider_rate_limited",
    "manual_research_required",
    "schema_repairable",
    "fatal",
]


class PipelineRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    pipeline_config_version_id: uuid.UUID | None
    run_type: str
    status: str
    trigger: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class JobRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    job_type: str
    queue: str
    status: str
    attempt: int
    max_attempts: int
    idempotency_key: str
    dedupe_key: str | None
    retry_class: str
    priority: int
    lease_owner: str | None
    lease_expires_at: datetime | None
    heartbeat_at: datetime | None
    scheduled_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    error_message: str | None
    trace_id: str | None


class EventEnvelope(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str
    event_version: str = "1.0"
    client_id: uuid.UUID
    pipeline_id: uuid.UUID | None = None
    run_id: uuid.UUID | None = None
    job_id: uuid.UUID | None = None
    correlation_id: uuid.UUID | None = None
    trace_id: str | None = None
    idempotency_key: str
    occurred_at: datetime
    producer: str
    payload: dict[str, Any] = Field(default_factory=dict)
