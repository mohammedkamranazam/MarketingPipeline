"""
Acceptance Criteria:
- SourceConnector has id (UUID PK), client_id, pipeline_id, source_type
  (public_web|search_provider|enrichment_provider|email_verification|outreach_export),
  name, base_url, adapter_key, status (active|paused|disabled), config_json (text),
  rate_limit_per_minute (int, nullable), and timestamps.
- PolicyRule has id, client_id, pipeline_id, entity_type (source|provider|url_pattern),
  entity_id (nullable), pattern (nullable), decision (allow|block|review),
  priority (int), reason, and timestamps.
- URLCandidate has id, client_id, pipeline_id, source_connector_id (FK, nullable),
  url (text, unique per pipeline), status (pending|allowed|blocked|review),
  policy_decision (allow|block|review|unknown), discovered_at, and timestamps.
- CredentialProfile has id, client_id, pipeline_id, name, adapter_key,
  status (active|expiring|expired|validation_failed|insufficient_scope|revoked|disabled),
  secret_reference (text — vault path or env key, never raw secret),
  scopes (text JSON), expires_at (nullable), last_validated_at (nullable),
  next_validation_at (nullable), rotation_due_at (nullable),
  masked_fingerprint (nullable), and timestamps.
- CredentialValidationRun has id, credential_profile_id (FK), status (passed|failed),
  reason (nullable), checked_scopes (text JSON), and created_at.
- AdapterRegistry has id, adapter_key (unique), display_name, source_type,
  terms_url (nullable), cost_model (nullable), timeout_seconds (int),
  retry_class (text), audit_event_type (text), and is_certified (bool).
- All records scoped by client_id and pipeline_id.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SourceConnector(Base):
    __tablename__ = "source_connectors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    adapter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    rate_limit_per_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)
    credential_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("credential_profiles.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    url_candidates: Mapped[list["URLCandidate"]] = relationship(
        "URLCandidate", back_populates="source_connector", cascade="all, delete-orphan"
    )
    credential_profile: Mapped["CredentialProfile | None"] = relationship(
        "CredentialProfile", back_populates="source_connectors"
    )


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    pattern: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )


class URLCandidate(Base):
    __tablename__ = "url_candidates"
    __table_args__ = (
        UniqueConstraint("pipeline_id", "url", name="uq_url_candidates_pipeline_url"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    source_connector_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("source_connectors.id", ondelete="SET NULL"), nullable=True
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    policy_decision: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    source_connector: Mapped["SourceConnector | None"] = relationship(
        "SourceConnector", back_populates="url_candidates"
    )


class CredentialProfile(Base):
    __tablename__ = "credential_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    adapter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="active")
    secret_reference: Mapped[str] = mapped_column(Text, nullable=False)
    scopes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_validated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_validation_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rotation_due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    masked_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    validation_runs: Mapped[list["CredentialValidationRun"]] = relationship(
        "CredentialValidationRun",
        back_populates="credential_profile",
        cascade="all, delete-orphan",
    )
    source_connectors: Mapped[list["SourceConnector"]] = relationship(
        "SourceConnector", back_populates="credential_profile"
    )


class CredentialValidationRun(Base):
    __tablename__ = "credential_validation_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    credential_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credential_profiles.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_scopes: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    credential_profile: Mapped["CredentialProfile"] = relationship(
        "CredentialProfile", back_populates="validation_runs"
    )


class AdapterRegistry(Base):
    __tablename__ = "adapter_registry"
    __table_args__ = (
        UniqueConstraint("adapter_key", name="uq_adapter_registry_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    adapter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    terms_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    retry_class: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    audit_event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_certified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
