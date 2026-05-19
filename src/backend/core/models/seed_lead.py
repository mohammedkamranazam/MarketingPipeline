"""
Acceptance Criteria:
- LeadImportBatch has id (UUID PK), client_id, pipeline_id (FK -> pipelines.id),
  filename, original_name, mime_type, size_bytes, storage_key, status,
  total_rows, valid_rows, error_rows, created_at, updated_at.
- LeadImportBatch status: pending|processing|completed|failed.
- SeedLeadRow has id, batch_id (FK -> lead_import_batches.id), client_id, pipeline_id,
  row_index (int), original_first_name (nullable), original_last_name (nullable),
  original_company (nullable), original_source (nullable), original_notes (nullable),
  raw_values (JSON text), normalized_first_name (nullable), normalized_last_name (nullable),
  normalized_company (nullable), normalized_source (nullable), status, validation_errors
  (JSON text), is_duplicate (bool), created_at.
- (batch_id, row_index) is unique.
- All pipeline-scoped rows include client_id and pipeline_id for isolation.
- All timestamps default to now() in UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class LeadImportBatch(Base):
    __tablename__ = "lead_import_batches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    rows: Mapped[list["SeedLeadRow"]] = relationship(
        "SeedLeadRow", back_populates="batch", cascade="all, delete-orphan"
    )


class SeedLeadRow(Base):
    __tablename__ = "seed_lead_rows"
    __table_args__ = (
        UniqueConstraint("batch_id", "row_index", name="uq_seed_lead_rows_batch_row"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lead_import_batches.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_company: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_values: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    normalized_first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    validation_errors: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    is_duplicate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    batch: Mapped["LeadImportBatch"] = relationship("LeadImportBatch", back_populates="rows")
