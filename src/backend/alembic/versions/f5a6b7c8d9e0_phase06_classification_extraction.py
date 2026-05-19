"""phase06_classification_extraction

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-05-19 00:00:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f5a6b7c8d9e0"
down_revision: str | None = "e4f5a6b7c8d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── page_classifications ──────────────────────────────────────────────────
    op.create_table(
        "page_classifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("crawl_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("page_type", sa.String(100), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("classifier", sa.String(50), nullable=False, server_default="rule"),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("schema_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["crawl_artifact_id"], ["crawl_artifacts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_page_classifications_pipeline_artifact",
        "page_classifications",
        ["pipeline_id", "crawl_artifact_id"],
    )
    op.create_index(
        "ix_page_classifications_pipeline_type",
        "page_classifications",
        ["pipeline_id", "page_type"],
    )

    # ── extracted_companies ───────────────────────────────────────────────────
    op.create_table(
        "extracted_companies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("crawl_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("seed_lead_row_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("domain", sa.String(512), nullable=True),
        sa.Column("industry", sa.String(255), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("evidence_url", sa.Text(), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("extractor", sa.String(50), nullable=False, server_default="rule"),
        sa.Column("schema_error", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["crawl_artifact_id"], ["crawl_artifacts.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["seed_lead_row_id"], ["seed_lead_rows.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extracted_companies_pipeline_id", "extracted_companies", ["pipeline_id"]
    )
    op.create_index(
        "ix_extracted_companies_pipeline_domain",
        "extracted_companies",
        ["pipeline_id", "domain"],
    )

    # ── extracted_signals ─────────────────────────────────────────────────────
    op.create_table(
        "extracted_signals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("extracted_company_id", sa.Uuid(), nullable=True),
        sa.Column("crawl_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("signal_type", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("evidence_url", sa.Text(), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("extractor", sa.String(50), nullable=False, server_default="rule"),
        sa.Column("schema_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["extracted_company_id"], ["extracted_companies.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["crawl_artifact_id"], ["crawl_artifacts.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extracted_signals_pipeline_id", "extracted_signals", ["pipeline_id"]
    )
    op.create_index(
        "ix_extracted_signals_pipeline_type",
        "extracted_signals",
        ["pipeline_id", "signal_type"],
    )

    # ── extracted_contacts ────────────────────────────────────────────────────
    op.create_table(
        "extracted_contacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("extracted_company_id", sa.Uuid(), nullable=True),
        sa.Column("crawl_artifact_id", sa.Uuid(), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("evidence_url", sa.Text(), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("extractor", sa.String(50), nullable=False, server_default="rule"),
        sa.Column("schema_error", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["extracted_company_id"], ["extracted_companies.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["crawl_artifact_id"], ["crawl_artifacts.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_extracted_contacts_pipeline_id", "extracted_contacts", ["pipeline_id"]
    )
    op.create_index(
        "ix_extracted_contacts_pipeline_company",
        "extracted_contacts",
        ["pipeline_id", "extracted_company_id"],
    )

    # ── profile_candidates ────────────────────────────────────────────────────
    op.create_table(
        "profile_candidates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("seed_lead_row_id", sa.Uuid(), nullable=False),
        sa.Column("extracted_company_id", sa.Uuid(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("domain_match", sa.String(512), nullable=True),
        sa.Column("title_match", sa.String(512), nullable=True),
        sa.Column("location_match", sa.String(512), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("evidence_url", sa.Text(), nullable=True),
        sa.Column("evidence_text", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["seed_lead_row_id"], ["seed_lead_rows.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["extracted_company_id"], ["extracted_companies.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_profile_candidates_pipeline_seed_lead",
        "profile_candidates",
        ["pipeline_id", "seed_lead_row_id"],
    )

    # ── enrichment_records ────────────────────────────────────────────────────
    op.create_table(
        "enrichment_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("profile_candidate_id", sa.Uuid(), nullable=True),
        sa.Column("extracted_contact_id", sa.Uuid(), nullable=True),
        sa.Column("adapter_key", sa.String(100), nullable=False),
        sa.Column("provider_request_id", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(512), nullable=True),
        sa.Column("phone", sa.String(100), nullable=True),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("company", sa.String(512), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("cost_credits", sa.Float(), nullable=True),
        sa.Column("provenance", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["profile_candidate_id"], ["profile_candidates.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["extracted_contact_id"], ["extracted_contacts.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enrichment_records_pipeline_id", "enrichment_records", ["pipeline_id"]
    )
    op.create_index(
        "ix_enrichment_records_pipeline_status",
        "enrichment_records",
        ["pipeline_id", "status"],
    )

    # ── email_verification_records ────────────────────────────────────────────
    op.create_table(
        "email_verification_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("enrichment_record_id", sa.Uuid(), nullable=True),
        sa.Column("adapter_key", sa.String(100), nullable=False),
        sa.Column("email", sa.String(512), nullable=False),
        sa.Column("verification_status", sa.String(50), nullable=False),
        sa.Column("deliverability", sa.String(50), nullable=True),
        sa.Column("is_risky", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("provider_request_id", sa.String(255), nullable=True),
        sa.Column("provenance", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["enrichment_record_id"], ["enrichment_records.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_email_verification_pipeline_id", "email_verification_records", ["pipeline_id"]
    )
    op.create_index(
        "ix_email_verification_pipeline_email",
        "email_verification_records",
        ["pipeline_id", "email"],
    )

    # ── research_summaries ────────────────────────────────────────────────────
    op.create_table(
        "research_summaries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("pipeline_id", sa.Uuid(), nullable=False),
        sa.Column("extracted_company_id", sa.Uuid(), nullable=True),
        sa.Column("summary_text", sa.Text(), nullable=False),
        sa.Column("citations_json", sa.Text(), nullable=True),
        sa.Column("generator", sa.String(50), nullable=False, server_default="llm"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pipeline_id"], ["pipelines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["extracted_company_id"], ["extracted_companies.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_summaries_pipeline_id", "research_summaries", ["pipeline_id"]
    )


def downgrade() -> None:
    op.drop_table("research_summaries")
    op.drop_table("email_verification_records")
    op.drop_table("enrichment_records")
    op.drop_table("profile_candidates")
    op.drop_table("extracted_contacts")
    op.drop_table("extracted_signals")
    op.drop_table("extracted_companies")
    op.drop_table("page_classifications")
