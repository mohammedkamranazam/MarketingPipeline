"""
Acceptance Criteria:
- Pipeline has id (UUID PK), client_id (FK -> clients.id), name (non-null), slug (non-null).
- (client_id, name) is unique — pipeline names are unique per client.
- Pipeline has lane (discovery|seed_enrichment), status (active|paused|archived),
  and lifecycle timestamps.
- PipelineSetting has id (UUID PK), pipeline_id (FK -> pipelines.id), key, value (text).
- (pipeline_id, key) is unique in pipeline_settings.
- PipelineConfigVersion has id, pipeline_id (FK), version_number (int),
  state (active|draft|superseded), snapshot (JSON text), created_at.
- Only one active config version per pipeline enforced at application layer.
- All timestamps default to now() in UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base
from core.models.client import Client


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Pipeline(Base):
    __tablename__ = "pipelines"
    __table_args__ = (
        UniqueConstraint("client_id", "name", name="uq_pipelines_client_name"),
        UniqueConstraint("client_id", "slug", name="uq_pipelines_client_slug"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    lane: Mapped[str] = mapped_column(String(50), nullable=False, default="discovery")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    client: Mapped["Client"] = relationship("Client", back_populates="pipelines")
    settings: Mapped[list["PipelineSetting"]] = relationship(
        "PipelineSetting", back_populates="pipeline", cascade="all, delete-orphan"
    )
    config_versions: Mapped[list["PipelineConfigVersion"]] = relationship(
        "PipelineConfigVersion", back_populates="pipeline", cascade="all, delete-orphan"
    )


class PipelineSetting(Base):
    __tablename__ = "pipeline_settings"
    __table_args__ = (
        UniqueConstraint("pipeline_id", "key", name="uq_pipeline_settings_pipeline_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="settings")


class PipelineConfigVersion(Base):
    __tablename__ = "pipeline_config_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="config_versions")
