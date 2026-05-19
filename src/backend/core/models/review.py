"""
Acceptance Criteria:
- ReviewItem has id (UUID PK), client_id, pipeline_id, source_document_id (nullable FK),
  source_knowledge_item_id (nullable FK), item_type, content, evidence_text,
  evidence_page (nullable), confidence (float), status, actor_id (nullable),
  actor_note (nullable), edited_content (nullable), created_at, decided_at (nullable),
  updated_at.
- ReviewItem status: pending | approved | rejected | edited_and_approved.
- ActiveICPConfig has id (UUID PK), client_id, pipeline_id (unique),
  pipeline_config_version_id (FK), vertical, target_company_size_min (nullable),
  target_company_size_max (nullable), geographies (JSON text list), titles (JSON text list),
  signals (JSON text list), exclusions (JSON text list), notes (nullable),
  activated_by (nullable), activated_at, created_at, updated_at.
- (pipeline_id) is unique in active_icp_configs — one active config per pipeline.
- SuppressionRule has id (UUID PK), client_id, pipeline_id, rule_type
  (domain | email | company | title), value, reason (nullable), added_by (nullable),
  created_at.
- EnrichmentGuardrail has id (UUID PK), client_id, pipeline_id, guardrail_type
  (enrichment_provider | email_verification | outreach_export), enabled (bool),
  policy_notes (nullable), approved_by (nullable), approved_at (nullable), created_at,
  updated_at.
- ConfigAuditLog has id (UUID PK), client_id, pipeline_id, actor_id (nullable),
  action, entity_type, entity_id (nullable), before_snapshot (nullable JSON text),
  after_snapshot (nullable JSON text), created_at.
- All pipeline-scoped records include client_id and pipeline_id.
- All timestamps default to now() in UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ReviewItem(Base):
    __tablename__ = "review_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    source_knowledge_item_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extracted_knowledge_items.id", ondelete="SET NULL"), nullable=True
    )
    item_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    actor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    edited_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class ActiveICPConfig(Base):
    __tablename__ = "active_icp_configs"
    __table_args__ = (
        UniqueConstraint("pipeline_id", name="uq_active_icp_configs_pipeline"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    pipeline_config_version_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    vertical: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_company_size_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_company_size_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geographies: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    titles: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    signals: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    exclusions: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    activated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class SuppressionRule(Base):
    __tablename__ = "suppression_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(512), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    added_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )


class EnrichmentGuardrail(Base):
    __tablename__ = "enrichment_guardrails"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    guardrail_type: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    policy_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class ConfigAuditLog(Base):
    __tablename__ = "config_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    before_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
