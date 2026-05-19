"""
Acceptance Criteria:
- CrawlJob has id (UUID PK), client_id, pipeline_id, source_connector_id (nullable FK),
  job_type, status, idempotency_key (unique), trigger, attempt, max_attempts,
  lease_owner (nullable), lease_expires_at (nullable), heartbeat_at (nullable),
  scheduled_at, started_at (nullable), finished_at (nullable),
  error_code (nullable), error_message (nullable), trace_id (nullable),
  rate_limit_per_minute (nullable), robots_txt_url (nullable),
  concurrency_budget (nullable), created_at, updated_at.
- CrawlArtifact has id (UUID PK), client_id, pipeline_id, crawl_job_id (nullable FK),
  source_connector_id (nullable FK), seed_lead_row_id (nullable FK),
  artifact_type, url (nullable), storage_key, content_hash (nullable),
  status, policy_decision (nullable), mime_type (nullable),
  size_bytes (nullable), raw_metadata_json (nullable),
  created_at, updated_at.
- CrawlArtifact has UniqueConstraint on (pipeline_id, content_hash) for deduplication.
- CrawlBudget has id (UUID PK), client_id, pipeline_id (nullable), source_connector_id (nullable),
  adapter_key (nullable), budget_type, max_concurrent, current_count, created_at, updated_at.
- All records scoped by client_id and pipeline_id.
- All timestamps default to now() in UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"
    __table_args__ = (
        Index("ix_crawl_jobs_pipeline_status", "pipeline_id", "status"),
        Index("ix_crawl_jobs_idempotency_key", "idempotency_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    source_connector_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_connectors.id", ondelete="SET NULL"), nullable=True
    )
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, default="crawl")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    idempotency_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    trigger: Mapped[str] = mapped_column(String(100), nullable=False, default="api")
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    lease_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rate_limit_per_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)
    robots_txt_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    concurrency_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class CrawlArtifact(Base):
    __tablename__ = "crawl_artifacts"
    __table_args__ = (
        UniqueConstraint("pipeline_id", "content_hash", name="uq_crawl_artifacts_pipeline_hash"),
        Index("ix_crawl_artifacts_pipeline_type", "pipeline_id", "artifact_type"),
        Index("ix_crawl_artifacts_crawl_job_id", "crawl_job_id"),
        Index("ix_crawl_artifacts_seed_lead_row_id", "seed_lead_row_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    crawl_job_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("crawl_jobs.id", ondelete="SET NULL"), nullable=True
    )
    source_connector_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_connectors.id", ondelete="SET NULL"), nullable=True
    )
    seed_lead_row_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("seed_lead_rows.id", ondelete="SET NULL"), nullable=True
    )
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="stored")
    policy_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class CrawlBudget(Base):
    __tablename__ = "crawl_budgets"
    __table_args__ = (
        Index("ix_crawl_budgets_pipeline_id", "pipeline_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=True
    )
    source_connector_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_connectors.id", ondelete="CASCADE"), nullable=True
    )
    adapter_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    budget_type: Mapped[str] = mapped_column(String(50), nullable=False)
    max_concurrent: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
