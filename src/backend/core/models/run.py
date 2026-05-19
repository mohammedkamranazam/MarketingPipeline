"""
Acceptance Criteria:
- PipelineRun has id (UUID PK), client_id, pipeline_id, pipeline_config_version_id (nullable),
  run_type, status, trigger, created_at, started_at (nullable), finished_at (nullable).
- JobRun has id (UUID PK), run_id (FK -> pipeline_runs.id), client_id, pipeline_id,
  job_type, queue, status, attempt, max_attempts, idempotency_key, dedupe_key (nullable),
  retry_class, priority, lease_owner (nullable), lease_expires_at (nullable),
  heartbeat_at (nullable), scheduled_at, started_at (nullable), finished_at (nullable),
  error_code (nullable), error_message (nullable), trace_id (nullable).
- EventOutbox has id, client_id, pipeline_id (nullable), run_id (nullable), job_id (nullable),
  event_type, event_version, payload (JSON text), idempotency_key, published_at (nullable),
  created_at.
- EventInbox has id, event_id (unique), event_type, idempotency_key (unique), processed_at,
  created_at.
- Retried jobs preserve job_id, increment attempt, retain idempotency_key.
- All timestamps default to now() in UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    pipeline_config_version_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    run_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    trigger: Mapped[str] = mapped_column(String(100), nullable=False, default="api")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    job_runs: Mapped[list["JobRun"]] = relationship(
        "JobRun", back_populates="pipeline_run", cascade="all, delete-orphan"
    )


class JobRun(Base):
    __tablename__ = "job_runs"
    __table_args__ = (
        Index("ix_job_runs_idempotency_key", "idempotency_key"),
        Index("ix_job_runs_queue_status", "queue", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    queue: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    idempotency_key: Mapped[str] = mapped_column(String(512), nullable=False)
    dedupe_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    retry_class: Mapped[str] = mapped_column(String(50), nullable=False, default="transient")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
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

    pipeline_run: Mapped["PipelineRun"] = relationship("PipelineRun", back_populates="job_runs")


class EventOutbox(Base):
    __tablename__ = "event_outbox"
    __table_args__ = (Index("ix_event_outbox_published_at", "published_at"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    job_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(512), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class EventInbox(Base):
    __tablename__ = "event_inbox"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
