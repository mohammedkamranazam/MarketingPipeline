"""phase05_crawl_artifacts

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-05-19 00:00:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: str | None = "d3e4f5a6b7c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "crawl_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("source_connector_id", sa.Uuid(), nullable=True),
        sa.Column("job_type", sa.String(100), nullable=False, server_default="crawl"),
        sa.Column("status", sa.String(50), nullable=False, server_default="queued"),
        sa.Column("idempotency_key", sa.String(512), nullable=False),
        sa.Column("trigger", sa.String(100), nullable=False, server_default="api"),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("lease_owner", sa.String(255), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("trace_id", sa.String(255), nullable=True),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=True),
        sa.Column("robots_txt_url", sa.Text(), nullable=True),
        sa.Column("concurrency_budget", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_connector_id"], ["source_connectors.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_crawl_jobs_idempotency_key"),
    )
    op.create_index("ix_crawl_jobs_pipeline_status", "crawl_jobs", ["pipeline_id", "status"])
    op.create_index("ix_crawl_jobs_idempotency_key", "crawl_jobs", ["idempotency_key"])

    op.create_table(
        "crawl_artifacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("crawl_job_id", sa.Uuid(), nullable=True),
        sa.Column("source_connector_id", sa.Uuid(), nullable=True),
        sa.Column("seed_lead_row_id", sa.Uuid(), nullable=True),
        sa.Column("artifact_type", sa.String(100), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="stored"),
        sa.Column("policy_decision", sa.String(50), nullable=True),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("raw_metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["crawl_job_id"], ["crawl_jobs.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["source_connector_id"], ["source_connectors.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["seed_lead_row_id"], ["seed_lead_rows.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "pipeline_id", "content_hash", name="uq_crawl_artifacts_pipeline_hash"
        ),
    )
    op.create_index(
        "ix_crawl_artifacts_pipeline_type", "crawl_artifacts", ["pipeline_id", "artifact_type"]
    )
    op.create_index("ix_crawl_artifacts_crawl_job_id", "crawl_artifacts", ["crawl_job_id"])
    op.create_index(
        "ix_crawl_artifacts_seed_lead_row_id", "crawl_artifacts", ["seed_lead_row_id"]
    )

    op.create_table(
        "crawl_budgets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=True),
        sa.Column("source_connector_id", sa.Uuid(), nullable=True),
        sa.Column("adapter_key", sa.String(100), nullable=True),
        sa.Column("budget_type", sa.String(50), nullable=False),
        sa.Column("max_concurrent", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("current_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["source_connector_id"], ["source_connectors.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crawl_budgets_pipeline_id", "crawl_budgets", ["pipeline_id"])


def downgrade() -> None:
    op.drop_table("crawl_budgets")
    op.drop_table("crawl_artifacts")
    op.drop_table("crawl_jobs")
