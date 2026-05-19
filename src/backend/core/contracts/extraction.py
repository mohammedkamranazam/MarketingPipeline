"""
Acceptance Criteria:
- All schemas use Pydantic v2 with strict typing; no `any`.
- PageClassificationResponse, ExtractedCompanyResponse, ExtractedSignalResponse,
  ExtractedContactResponse carry evidence_url and evidence_text.
- ProfileCandidateResponse carries rank, domain/title/location match, confidence.
- EnrichmentRecordResponse carries email, phone, title, company, linkedin_url,
  cost_credits, provenance, provider_request_id, status.
- EmailVerificationResponse carries verification_status, deliverability, is_risky,
  reason, provenance, provider_request_id.
- ResearchSummaryResponse carries summary_text, citations_json, generator.
- Create/update schemas for each entity.
- Extraction workflow request/response schemas.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

ReviewStatus = Literal["pending", "approved", "rejected", "follow_up"]
Extractor = Literal["rule", "mock_llm", "llm"]
VerificationStatus = Literal["verified", "risky", "invalid", "unknown"]
Deliverability = Literal["deliverable", "risky", "undeliverable", "unknown"]
EnrichmentStatus = Literal["pending", "completed", "failed"]


# ── PageClassification ────────────────────────────────────────────────────────

class PageClassificationResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    crawl_artifact_id: uuid.UUID
    page_type: str
    relevance_score: float
    classifier: str
    confidence: float | None
    schema_error: str | None
    created_at: datetime
    updated_at: datetime


class ClassifyArtifactRequest(BaseModel):
    crawl_artifact_id: uuid.UUID
    use_llm_fallback: bool = False


# ── ExtractedCompany ──────────────────────────────────────────────────────────

class ExtractedCompanyResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    crawl_artifact_id: uuid.UUID | None
    seed_lead_row_id: uuid.UUID | None
    name: str
    domain: str | None
    industry: str | None
    employee_count: int | None
    location: str | None
    description: str | None
    confidence: float
    evidence_url: str | None
    evidence_text: str | None
    extractor: str
    schema_error: str | None
    review_status: str
    created_at: datetime
    updated_at: datetime


class ExtractCompaniesRequest(BaseModel):
    crawl_artifact_id: uuid.UUID
    use_llm_fallback: bool = False


class ExtractedCompanyUpdate(BaseModel):
    review_status: ReviewStatus | None = None
    name: str | None = None
    domain: str | None = None
    industry: str | None = None


# ── ExtractedSignal ───────────────────────────────────────────────────────────

class ExtractedSignalResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    extracted_company_id: uuid.UUID | None
    crawl_artifact_id: uuid.UUID | None
    signal_type: str
    value: str | None
    confidence: float
    evidence_url: str | None
    evidence_text: str | None
    extractor: str
    schema_error: str | None
    created_at: datetime
    updated_at: datetime


class ExtractSignalsRequest(BaseModel):
    crawl_artifact_id: uuid.UUID
    extracted_company_id: uuid.UUID | None = None
    use_llm_fallback: bool = False


# ── ExtractedContact ──────────────────────────────────────────────────────────

class ExtractedContactResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    extracted_company_id: uuid.UUID | None
    crawl_artifact_id: uuid.UUID | None
    first_name: str | None
    last_name: str | None
    title: str | None
    linkedin_url: str | None
    confidence: float
    evidence_url: str | None
    evidence_text: str | None
    extractor: str
    schema_error: str | None
    review_status: str
    created_at: datetime
    updated_at: datetime


class ExtractContactsRequest(BaseModel):
    crawl_artifact_id: uuid.UUID
    extracted_company_id: uuid.UUID | None = None
    use_llm_fallback: bool = False


# ── ProfileCandidate ──────────────────────────────────────────────────────────

class ProfileCandidateResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    seed_lead_row_id: uuid.UUID
    extracted_company_id: uuid.UUID | None
    rank: int
    domain_match: str | None
    title_match: str | None
    location_match: str | None
    confidence: float
    evidence_url: str | None
    evidence_text: str | None
    review_status: str
    created_at: datetime
    updated_at: datetime


class RankProfileCandidatesRequest(BaseModel):
    seed_lead_row_id: uuid.UUID


# ── EnrichmentRecord ──────────────────────────────────────────────────────────

class EnrichmentRecordResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    profile_candidate_id: uuid.UUID | None
    extracted_contact_id: uuid.UUID | None
    adapter_key: str
    provider_request_id: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None
    title: str | None
    company: str | None
    linkedin_url: str | None
    cost_credits: float | None
    provenance: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class EnrichContactRequest(BaseModel):
    profile_candidate_id: uuid.UUID | None = None
    extracted_contact_id: uuid.UUID | None = None
    first_name: str = Field(min_length=1)
    last_name: str | None = None
    company: str | None = None
    domain: str | None = None
    title: str | None = None
    adapter_key: str = "mock_enrichment"


# ── EmailVerification ─────────────────────────────────────────────────────────

class EmailVerificationResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    enrichment_record_id: uuid.UUID | None
    adapter_key: str
    email: str
    verification_status: str
    deliverability: str | None
    is_risky: bool
    reason: str | None
    provider_request_id: str | None
    provenance: str | None
    created_at: datetime
    updated_at: datetime


class VerifyEmailRequest(BaseModel):
    enrichment_record_id: uuid.UUID | None = None
    email: str = Field(min_length=5)
    adapter_key: str = "mock_email_verifier"


# ── ResearchSummary ───────────────────────────────────────────────────────────

class ResearchSummaryResponse(_OrmBase):
    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    extracted_company_id: uuid.UUID | None
    summary_text: str
    citations_json: str | None
    generator: str
    created_at: datetime
    updated_at: datetime


class GenerateSummaryRequest(BaseModel):
    extracted_company_id: uuid.UUID
    evidence_urls: list[str] = Field(default_factory=list)


# ── Extraction workflow ───────────────────────────────────────────────────────

class RunExtractionRequest(BaseModel):
    crawl_artifact_id: uuid.UUID
    use_llm_fallback: bool = False


class RunExtractionResponse(BaseModel):
    classification: PageClassificationResponse
    companies: list[ExtractedCompanyResponse]
    signals: list[ExtractedSignalResponse]
    contacts: list[ExtractedContactResponse]
