"""
Acceptance Criteria:
- classify_artifact(db, client_id, pipeline_id, artifact_id, use_llm_fallback)
  classifies using rule classifier first; falls back to MockLLMAdapter when
  use_llm_fallback=True or rule returns low confidence (<0.5).
- Rule classifier: sets page_type based on URL path keywords, relevance_score
  based on content keywords.
- extract_companies(db, client_id, pipeline_id, artifact_id, use_llm_fallback)
  extracts one ExtractedCompany per artifact via rule or LLM.
- extract_signals(db, client_id, pipeline_id, artifact_id, company_id, use_llm_fallback)
  extracts signals. Returns [] if no signals found.
- extract_contacts(db, client_id, pipeline_id, artifact_id, company_id, use_llm_fallback)
  extracts contacts. No email/phone created by extractor.
- run_extraction(db, client_id, pipeline_id, artifact_id, use_llm_fallback)
  runs classify → extract_companies → extract_signals → extract_contacts in order.
- list_companies(db, client_id, pipeline_id, review_status?) returns filtered list.
- get_company(db, client_id, pipeline_id, company_id) returns record or None.
- list_signals(db, client_id, pipeline_id, company_id?) returns filtered list.
- list_contacts(db, client_id, pipeline_id, company_id?) returns filtered list.
- resolve_seed_lead_companies(db, client_id, pipeline_id, seed_lead_row_id)
  finds or creates an ExtractedCompany from normalized_company and normalized_source.
- rank_profile_candidates(db, client_id, pipeline_id, seed_lead_row_id)
  scores company matches by domain, title, location similarity and stores ranked
  ProfileCandidate rows.
- enrich_contact(db, client_id, pipeline_id, request) calls MockEnrichmentAdapter
  and stores EnrichmentRecord.
- verify_email(db, client_id, pipeline_id, request) calls MockEmailVerifierAdapter
  and stores EmailVerificationRecord.
- generate_summary(db, client_id, pipeline_id, request) calls MockLLMAdapter
  summarize and stores ResearchSummary.
- All queries include both client_id and pipeline_id filters.
- No TypeScript any.
"""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.adapters.base import AdapterInput
from core.adapters.mock_email_verifier import MockEmailVerifierAdapter
from core.adapters.mock_enrichment import MockEnrichmentAdapter
from core.adapters.mock_llm import MockLLMAdapter
from core.contracts.extraction import (
    EnrichContactRequest,
    GenerateSummaryRequest,
    PageClassificationResponse,
    RunExtractionResponse,
    VerifyEmailRequest,
)
from core.models.crawl import CrawlArtifact
from core.models.extraction import (
    EmailVerificationRecord,
    EnrichmentRecord,
    ExtractedCompany,
    ExtractedContact,
    ExtractedSignal,
    PageClassification,
    ProfileCandidate,
    ResearchSummary,
)
from core.models.seed_lead import SeedLeadRow

_llm = MockLLMAdapter()
_enricher = MockEnrichmentAdapter()
_verifier = MockEmailVerifierAdapter()

_PAGE_TYPE_KEYWORDS: dict[str, list[str]] = {
    "team_page": ["team", "about/team", "people", "leadership", "staff"],
    "pricing_page": ["pricing", "plans", "subscribe"],
    "blog_post": ["blog", "news", "article", "post"],
    "about_page": ["about", "company", "mission", "story"],
    "company_homepage": [],
}
_RELEVANCE_KEYWORDS = [
    "saas", "software", "platform", "enterprise", "cloud", "api", "b2b",
    "solution", "integration", "workflow", "automation",
]


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _rule_classify(content: str, url: str) -> dict:
    path = urlparse(url).path.lower() if url else ""
    page_type = "company_homepage"
    for ptype, keywords in _PAGE_TYPE_KEYWORDS.items():
        if any(kw in path for kw in keywords):
            page_type = ptype
            break
    lower = content.lower()
    match_count = sum(1 for kw in _RELEVANCE_KEYWORDS if kw in lower)
    relevance_score = min(1.0, 0.3 + match_count * 0.1)
    confidence = 0.7 if match_count >= 2 else 0.45
    return {
        "page_type": page_type,
        "relevance_score": relevance_score,
        "confidence": confidence,
        "classifier": "rule",
    }


def _rule_extract_company(content: str, url: str) -> dict:
    domain: str | None = None
    if url:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").split(":")[0] or None
    slug = domain.split(".")[0].title() if domain else "Unknown"
    lower = content.lower()
    industry: str | None = None
    if "saas" in lower or "software" in lower:
        industry = "Software"
    elif "healthcare" in lower or "medical" in lower:
        industry = "Healthcare"
    return {
        "name": f"{slug} Inc",
        "domain": domain,
        "industry": industry,
        "employee_count": None,
        "location": None,
        "description": None,
        "confidence": 0.65,
        "evidence_url": url or None,
        "evidence_text": content[:150] if content else None,
        "extractor": "rule",
        "schema_error": None,
    }


def _rule_extract_signals(content: str) -> list[dict]:
    lower = content.lower()
    signals = []
    if "hiring" in lower or "career" in lower or "job" in lower:
        signals.append({
            "signal_type": "hiring",
            "value": "Hiring signals detected",
            "confidence": 0.75,
            "evidence_text": "Hiring keywords found in content",
            "extractor": "rule",
        })
    if "funding" in lower or "series" in lower or "raised" in lower:
        signals.append({
            "signal_type": "funding",
            "value": "Funding signals detected",
            "confidence": 0.70,
            "evidence_text": "Funding keywords found in content",
            "extractor": "rule",
        })
    return signals


# ── Classification ────────────────────────────────────────────────────────────

def classify_artifact(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
    use_llm_fallback: bool = False,
) -> PageClassification:
    artifact = db.get(CrawlArtifact, artifact_id)
    if artifact is None or artifact.pipeline_id != pipeline_id:
        raise ValueError(f"Artifact {artifact_id} not found in pipeline {pipeline_id}")

    content = artifact.raw_metadata_json or ""
    url = artifact.url or ""
    result = _rule_classify(content, url)

    if use_llm_fallback or (result["confidence"] or 0) < 0.5:
        llm_out = _llm.execute(AdapterInput("classify", {"content": content, "url": url}))
        if llm_out.success:
            result = llm_out.data_dict()
            result.setdefault("classifier", "mock_llm")

    now = _utcnow()
    classification = PageClassification(
        client_id=client_id,
        pipeline_id=pipeline_id,
        crawl_artifact_id=artifact_id,
        page_type=result["page_type"],
        relevance_score=float(result.get("relevance_score", 0.0)),
        classifier=result.get("classifier", "rule"),
        confidence=result.get("confidence"),
        created_at=now,
        updated_at=now,
    )
    db.add(classification)
    db.flush()
    return classification


# ── Company extraction ────────────────────────────────────────────────────────

def extract_companies(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
    use_llm_fallback: bool = False,
) -> list[ExtractedCompany]:
    artifact = db.get(CrawlArtifact, artifact_id)
    if artifact is None or artifact.pipeline_id != pipeline_id:
        raise ValueError(f"Artifact {artifact_id} not found in pipeline {pipeline_id}")

    content = artifact.raw_metadata_json or ""
    url = artifact.url or ""
    data = _rule_extract_company(content, url)

    if use_llm_fallback or data["confidence"] < 0.5:
        llm_out = _llm.execute(
            AdapterInput("extract_company", {"content": content, "url": url})
        )
        if llm_out.success:
            data = llm_out.data_dict()

    now = _utcnow()
    company = ExtractedCompany(
        client_id=client_id,
        pipeline_id=pipeline_id,
        crawl_artifact_id=artifact_id,
        name=data["name"],
        domain=data.get("domain"),
        industry=data.get("industry"),
        employee_count=data.get("employee_count"),
        location=data.get("location"),
        description=data.get("description"),
        confidence=float(data.get("confidence", 0.0)),
        evidence_url=data.get("evidence_url"),
        evidence_text=data.get("evidence_text"),
        extractor=data.get("extractor", "rule"),
        schema_error=data.get("schema_error"),
        created_at=now,
        updated_at=now,
    )
    db.add(company)
    db.flush()
    return [company]


# ── Signal extraction ─────────────────────────────────────────────────────────

def extract_signals(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
    use_llm_fallback: bool = False,
) -> list[ExtractedSignal]:
    artifact = db.get(CrawlArtifact, artifact_id)
    if artifact is None or artifact.pipeline_id != pipeline_id:
        raise ValueError(f"Artifact {artifact_id} not found in pipeline {pipeline_id}")

    content = artifact.raw_metadata_json or ""
    signal_dicts = _rule_extract_signals(content)

    if use_llm_fallback or not signal_dicts:
        llm_out = _llm.execute(AdapterInput("extract_signals", {"content": content}))
        if llm_out.success:
            signal_dicts = llm_out.data_dict().get("signals", [])

    now = _utcnow()
    records = []
    for s in signal_dicts:
        sig = ExtractedSignal(
            client_id=client_id,
            pipeline_id=pipeline_id,
            extracted_company_id=company_id,
            crawl_artifact_id=artifact_id,
            signal_type=s["signal_type"],
            value=s.get("value"),
            confidence=float(s.get("confidence", 0.0)),
            evidence_url=s.get("evidence_url"),
            evidence_text=s.get("evidence_text"),
            extractor=s.get("extractor", "rule"),
            schema_error=s.get("schema_error"),
            created_at=now,
            updated_at=now,
        )
        db.add(sig)
        records.append(sig)
    db.flush()
    return records


# ── Contact extraction ────────────────────────────────────────────────────────

def extract_contacts(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
    use_llm_fallback: bool = False,
) -> list[ExtractedContact]:
    artifact = db.get(CrawlArtifact, artifact_id)
    if artifact is None or artifact.pipeline_id != pipeline_id:
        raise ValueError(f"Artifact {artifact_id} not found in pipeline {pipeline_id}")

    content = artifact.raw_metadata_json or ""
    url = artifact.url or ""
    contact_dicts: list[dict] = []

    if use_llm_fallback:
        llm_out = _llm.execute(
            AdapterInput("extract_contacts", {"content": content, "url": url})
        )
        if llm_out.success:
            contact_dicts = llm_out.data_dict().get("contacts", [])

    now = _utcnow()
    records = []
    for c in contact_dicts:
        contact = ExtractedContact(
            client_id=client_id,
            pipeline_id=pipeline_id,
            extracted_company_id=company_id,
            crawl_artifact_id=artifact_id,
            first_name=c.get("first_name"),
            last_name=c.get("last_name"),
            title=c.get("title"),
            linkedin_url=c.get("linkedin_url"),
            confidence=float(c.get("confidence", 0.0)),
            evidence_url=c.get("evidence_url"),
            evidence_text=c.get("evidence_text"),
            extractor=c.get("extractor", "mock_llm"),
            schema_error=c.get("schema_error"),
            created_at=now,
            updated_at=now,
        )
        db.add(contact)
        records.append(contact)
    db.flush()
    return records


# ── Full extraction workflow ──────────────────────────────────────────────────

def run_extraction(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
    use_llm_fallback: bool = False,
) -> RunExtractionResponse:
    classification = classify_artifact(db, client_id, pipeline_id, artifact_id, use_llm_fallback)
    companies = extract_companies(db, client_id, pipeline_id, artifact_id, use_llm_fallback)
    company_id = companies[0].id if companies else None
    signals = extract_signals(
        db, client_id, pipeline_id, artifact_id, company_id, use_llm_fallback
    )
    contacts = extract_contacts(
        db, client_id, pipeline_id, artifact_id, company_id, use_llm_fallback
    )
    from core.contracts.extraction import (
        ExtractedCompanyResponse,
        ExtractedContactResponse,
        ExtractedSignalResponse,
    )
    return RunExtractionResponse(
        classification=PageClassificationResponse.model_validate(classification),
        companies=[ExtractedCompanyResponse.model_validate(c) for c in companies],
        signals=[ExtractedSignalResponse.model_validate(s) for s in signals],
        contacts=[ExtractedContactResponse.model_validate(c) for c in contacts],
    )


# ── Retrieval ─────────────────────────────────────────────────────────────────

def list_companies(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    review_status: str | None = None,
) -> list[ExtractedCompany]:
    stmt = select(ExtractedCompany).where(
        ExtractedCompany.client_id == client_id,
        ExtractedCompany.pipeline_id == pipeline_id,
    )
    if review_status:
        stmt = stmt.where(ExtractedCompany.review_status == review_status)
    return list(db.scalars(stmt).all())


def get_company(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID,
) -> ExtractedCompany | None:
    company = db.get(ExtractedCompany, company_id)
    if company is None or company.pipeline_id != pipeline_id or company.client_id != client_id:
        return None
    return company


def list_signals(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
) -> list[ExtractedSignal]:
    stmt = select(ExtractedSignal).where(
        ExtractedSignal.client_id == client_id,
        ExtractedSignal.pipeline_id == pipeline_id,
    )
    if company_id:
        stmt = stmt.where(ExtractedSignal.extracted_company_id == company_id)
    return list(db.scalars(stmt).all())


def list_contacts(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
) -> list[ExtractedContact]:
    stmt = select(ExtractedContact).where(
        ExtractedContact.client_id == client_id,
        ExtractedContact.pipeline_id == pipeline_id,
    )
    if company_id:
        stmt = stmt.where(ExtractedContact.extracted_company_id == company_id)
    return list(db.scalars(stmt).all())


# ── Seed lead resolver + profile candidate ranking ────────────────────────────

def resolve_seed_lead_companies(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    seed_lead_row_id: uuid.UUID,
) -> list[ExtractedCompany]:
    row = db.get(SeedLeadRow, seed_lead_row_id)
    if row is None or row.pipeline_id != pipeline_id:
        raise ValueError(f"SeedLeadRow {seed_lead_row_id} not found in pipeline {pipeline_id}")

    company_name = row.normalized_company or row.original_company or "Unknown"
    domain: str | None = None
    if row.normalized_source and "." in row.normalized_source:
        domain = row.normalized_source.lower()

    now = _utcnow()
    company = ExtractedCompany(
        client_id=client_id,
        pipeline_id=pipeline_id,
        seed_lead_row_id=seed_lead_row_id,
        name=company_name,
        domain=domain,
        confidence=0.60,
        evidence_text=f"Resolved from seed lead row {seed_lead_row_id}",
        extractor="rule",
        created_at=now,
        updated_at=now,
    )
    db.add(company)
    db.flush()
    return [company]


def rank_profile_candidates(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    seed_lead_row_id: uuid.UUID,
) -> list[ProfileCandidate]:
    row = db.get(SeedLeadRow, seed_lead_row_id)
    if row is None or row.pipeline_id != pipeline_id:
        raise ValueError(f"SeedLeadRow {seed_lead_row_id} not found in pipeline {pipeline_id}")

    stmt = select(ExtractedCompany).where(
        ExtractedCompany.client_id == client_id,
        ExtractedCompany.pipeline_id == pipeline_id,
    )
    companies = list(db.scalars(stmt).all())

    now = _utcnow()
    candidates = []
    for rank_idx, company in enumerate(companies):
        domain_match: str | None = None
        title_match: str | None = None
        location_match: str | None = None
        score = 0.3

        if company.domain and row.normalized_company:
            slug = company.domain.split(".")[0].lower()
            if slug in (row.normalized_company or "").lower():
                domain_match = company.domain
                score += 0.3

        if company.location:
            location_match = company.location
            score += 0.1

        candidate = ProfileCandidate(
            client_id=client_id,
            pipeline_id=pipeline_id,
            seed_lead_row_id=seed_lead_row_id,
            extracted_company_id=company.id,
            rank=rank_idx,
            domain_match=domain_match,
            title_match=title_match,
            location_match=location_match,
            confidence=min(1.0, score),
            evidence_text=f"Ranked against seed lead {seed_lead_row_id}",
            created_at=now,
            updated_at=now,
        )
        db.add(candidate)
        candidates.append(candidate)
    db.flush()
    return candidates


def list_profile_candidates(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    seed_lead_row_id: uuid.UUID | None = None,
) -> list[ProfileCandidate]:
    stmt = select(ProfileCandidate).where(
        ProfileCandidate.client_id == client_id,
        ProfileCandidate.pipeline_id == pipeline_id,
    )
    if seed_lead_row_id:
        stmt = stmt.where(ProfileCandidate.seed_lead_row_id == seed_lead_row_id)
    stmt = stmt.order_by(ProfileCandidate.rank)
    return list(db.scalars(stmt).all())


# ── Enrichment ────────────────────────────────────────────────────────────────

def enrich_contact(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    request: EnrichContactRequest,
) -> EnrichmentRecord:
    out = _enricher.execute(AdapterInput("enrich_contact", {
        "first_name": request.first_name,
        "last_name": request.last_name or "",
        "company": request.company or "",
        "domain": request.domain or "example.com",
        "title": request.title or "",
    }))
    now = _utcnow()
    data = out.data_dict() if out.success else {}
    record = EnrichmentRecord(
        client_id=client_id,
        pipeline_id=pipeline_id,
        profile_candidate_id=request.profile_candidate_id,
        extracted_contact_id=request.extracted_contact_id,
        adapter_key=request.adapter_key,
        provider_request_id=data.get("provider_request_id"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=data.get("email"),
        phone=data.get("phone"),
        title=data.get("title"),
        company=data.get("company"),
        linkedin_url=data.get("linkedin_url"),
        cost_credits=data.get("cost_credits"),
        provenance=data.get("provenance"),
        status="completed" if out.success else "failed",
        error_message=out.error if not out.success else None,
        created_at=now,
        updated_at=now,
    )
    db.add(record)
    db.flush()
    return record


def list_enrichment_records(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = None,
) -> list[EnrichmentRecord]:
    stmt = select(EnrichmentRecord).where(
        EnrichmentRecord.client_id == client_id,
        EnrichmentRecord.pipeline_id == pipeline_id,
    )
    if status:
        stmt = stmt.where(EnrichmentRecord.status == status)
    return list(db.scalars(stmt).all())


# ── Email verification ────────────────────────────────────────────────────────

def verify_email(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    request: VerifyEmailRequest,
) -> EmailVerificationRecord:
    out = _verifier.execute(AdapterInput("verify_email", {"email": request.email}))
    data = out.data_dict() if out.success else {}
    now = _utcnow()
    record = EmailVerificationRecord(
        client_id=client_id,
        pipeline_id=pipeline_id,
        enrichment_record_id=request.enrichment_record_id,
        adapter_key=request.adapter_key,
        email=request.email,
        verification_status=data.get("verification_status", "unknown"),
        deliverability=data.get("deliverability"),
        is_risky=bool(data.get("is_risky", False)),
        reason=data.get("reason"),
        provider_request_id=data.get("provider_request_id"),
        provenance=data.get("provenance"),
        created_at=now,
        updated_at=now,
    )
    db.add(record)
    db.flush()
    return record


def list_verification_records(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = None,
) -> list[EmailVerificationRecord]:
    stmt = select(EmailVerificationRecord).where(
        EmailVerificationRecord.client_id == client_id,
        EmailVerificationRecord.pipeline_id == pipeline_id,
    )
    if status:
        stmt = stmt.where(EmailVerificationRecord.verification_status == status)
    return list(db.scalars(stmt).all())


# ── Research summaries ────────────────────────────────────────────────────────

def generate_summary(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    request: GenerateSummaryRequest,
) -> ResearchSummary:
    company = db.get(ExtractedCompany, request.extracted_company_id)
    if company is None or company.pipeline_id != pipeline_id:
        raise ValueError(
            f"Company {request.extracted_company_id} not found in pipeline {pipeline_id}"
        )

    out = _llm.execute(AdapterInput("summarize", {
        "company_name": company.name,
        "evidence_urls": request.evidence_urls,
    }))
    data = out.data_dict() if out.success else {}
    citations = data.get("citations", [])
    now = _utcnow()
    summary = ResearchSummary(
        client_id=client_id,
        pipeline_id=pipeline_id,
        extracted_company_id=request.extracted_company_id,
        summary_text=data.get("summary_text", "Summary unavailable."),
        citations_json=json.dumps(citations) if citations else None,
        generator=data.get("generator", "mock_llm"),
        created_at=now,
        updated_at=now,
    )
    db.add(summary)
    db.flush()
    return summary


def list_summaries(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID | None = None,
) -> list[ResearchSummary]:
    stmt = select(ResearchSummary).where(
        ResearchSummary.client_id == client_id,
        ResearchSummary.pipeline_id == pipeline_id,
    )
    if company_id:
        stmt = stmt.where(ResearchSummary.extracted_company_id == company_id)
    return list(db.scalars(stmt).all())


# ── Response helpers ──────────────────────────────────────────────────────────

def _company_to_response(c: ExtractedCompany) -> dict:
    from core.contracts.extraction import ExtractedCompanyResponse
    return ExtractedCompanyResponse.model_validate(c).model_dump()


def _signal_to_response(s: ExtractedSignal) -> dict:
    from core.contracts.extraction import ExtractedSignalResponse
    return ExtractedSignalResponse.model_validate(s).model_dump()


def _contact_to_response(c: ExtractedContact) -> dict:
    from core.contracts.extraction import ExtractedContactResponse
    return ExtractedContactResponse.model_validate(c).model_dump()
