"""
Acceptance Criteria:
- PageClassification links to CrawlArtifact, carries page_type, relevance_score,
  classifier, confidence, schema_error.
- ExtractedCompany carries name, domain, industry, employee_count, location,
  description, confidence, evidence_url, evidence_text, extractor, schema_error,
  review_status. Links to artifact and seed_lead_row.
- ExtractedSignal carries signal_type, value, confidence, evidence, extractor.
  Links to ExtractedCompany and CrawlArtifact.
- ExtractedContact carries first_name, last_name, title, linkedin_url, confidence,
  evidence, extractor, schema_error, review_status. Links to ExtractedCompany.
- ProfileCandidate links SeedLeadRow to ExtractedCompany with rank, domain/title/
  location match, confidence, evidence, review_status.
- EnrichmentRecord carries provider output (email, phone, title, company, linkedin_url),
  adapter_key, provenance, cost_credits, status, error_message.
- EmailVerificationRecord carries email, verification_status, deliverability, is_risky,
  reason, provenance, adapter_key.
- ResearchSummary carries summary_text, citations_json, generator.
- All records scoped by client_id and pipeline_id.
- No TypeScript any.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class PageClassification(Base):
    __tablename__ = "page_classifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    crawl_artifact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crawl_artifacts.id", ondelete="CASCADE"), nullable=False
    )
    page_type: Mapped[str] = mapped_column(String(100), nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    classifier: Mapped[str] = mapped_column(String(50), default="rule", nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    schema_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class ExtractedCompany(Base):
    __tablename__ = "extracted_companies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    crawl_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("crawl_artifacts.id", ondelete="SET NULL"), nullable=True
    )
    seed_lead_row_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("seed_lead_rows.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(512), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extractor: Mapped[str] = mapped_column(String(50), default="rule", nullable=False)
    schema_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class ExtractedSignal(Base):
    __tablename__ = "extracted_signals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    extracted_company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extracted_companies.id", ondelete="SET NULL"), nullable=True
    )
    crawl_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("crawl_artifacts.id", ondelete="SET NULL"), nullable=True
    )
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extractor: Mapped[str] = mapped_column(String(50), default="rule", nullable=False)
    schema_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class ExtractedContact(Base):
    __tablename__ = "extracted_contacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    extracted_company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extracted_companies.id", ondelete="SET NULL"), nullable=True
    )
    crawl_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("crawl_artifacts.id", ondelete="SET NULL"), nullable=True
    )
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extractor: Mapped[str] = mapped_column(String(50), default="rule", nullable=False)
    schema_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class ProfileCandidate(Base):
    __tablename__ = "profile_candidates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    seed_lead_row_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("seed_lead_rows.id", ondelete="CASCADE"), nullable=False
    )
    extracted_company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extracted_companies.id", ondelete="SET NULL"), nullable=True
    )
    rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    domain_match: Mapped[str | None] = mapped_column(String(512), nullable=True)
    title_match: Mapped[str | None] = mapped_column(String(512), nullable=True)
    location_match: Mapped[str | None] = mapped_column(String(512), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class EnrichmentRecord(Base):
    __tablename__ = "enrichment_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    profile_candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("profile_candidates.id", ondelete="SET NULL"), nullable=True
    )
    extracted_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extracted_contacts.id", ondelete="SET NULL"), nullable=True
    )
    adapter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    company: Mapped[str | None] = mapped_column(String(512), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost_credits: Mapped[float | None] = mapped_column(Float, nullable=True)
    provenance: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class EmailVerificationRecord(Base):
    __tablename__ = "email_verification_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    enrichment_record_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("enrichment_records.id", ondelete="SET NULL"), nullable=True
    )
    adapter_key: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(512), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=False)
    deliverability: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_risky: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provenance: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )


class ResearchSummary(Base):
    __tablename__ = "research_summaries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False
    )
    extracted_company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("extracted_companies.id", ondelete="SET NULL"), nullable=True
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    citations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    generator: Mapped[str] = mapped_column(String(50), default="llm", nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow, nullable=False
    )
