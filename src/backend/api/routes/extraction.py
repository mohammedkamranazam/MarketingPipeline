"""
Acceptance Criteria:
- POST /clients/{cid}/pipelines/{pid}/extraction/run runs full extraction workflow.
- GET /clients/{cid}/pipelines/{pid}/extraction/companies returns company list.
- GET /clients/{cid}/pipelines/{pid}/extraction/companies/{id} returns company or 404.
- GET /clients/{cid}/pipelines/{pid}/extraction/signals returns signals list.
- GET /clients/{cid}/pipelines/{pid}/extraction/contacts returns contacts list.
- POST /clients/{cid}/pipelines/{pid}/extraction/classify classifies one artifact.
- GET /clients/{cid}/pipelines/{pid}/extraction/profile-candidates returns candidates.
- POST /clients/{cid}/pipelines/{pid}/extraction/rank-profiles ranks for a seed lead row.
- POST /clients/{cid}/pipelines/{pid}/enrichment enrich a contact.
- GET /clients/{cid}/pipelines/{pid}/enrichment returns enrichment records.
- POST /clients/{cid}/pipelines/{pid}/email-verification verifies an email.
- GET /clients/{cid}/pipelines/{pid}/email-verification returns verification records.
- POST /clients/{cid}/pipelines/{pid}/research-summaries generates a summary.
- GET /clients/{cid}/pipelines/{pid}/research-summaries returns summaries.
- All routes return typed Pydantic responses; no untyped dicts.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.contracts.extraction import (
    ClassifyArtifactRequest,
    EmailVerificationResponse,
    EnrichContactRequest,
    EnrichmentRecordResponse,
    ExtractCompaniesRequest,
    ExtractContactsRequest,
    ExtractedCompanyResponse,
    ExtractedContactResponse,
    ExtractedSignalResponse,
    ExtractSignalsRequest,
    GenerateSummaryRequest,
    PageClassificationResponse,
    ProfileCandidateResponse,
    RankProfileCandidatesRequest,
    ResearchSummaryResponse,
    RunExtractionRequest,
    RunExtractionResponse,
    VerifyEmailRequest,
)
from core.db.session import get_db
from core.services import extraction_service as svc

router = APIRouter(tags=["extraction"])

_PREFIX = "/clients/{client_id}/pipelines/{pipeline_id}"


# ── Full extraction workflow ──────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/extraction/run",
    response_model=RunExtractionResponse,
    status_code=201,
)
def run_extraction(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: RunExtractionRequest,
    db: Session = Depends(get_db),
) -> RunExtractionResponse:
    try:
        return svc.run_extraction(
            db, client_id, pipeline_id, body.crawl_artifact_id, body.use_llm_fallback
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Classification ────────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/extraction/classify",
    response_model=PageClassificationResponse,
    status_code=201,
)
def classify_artifact(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: ClassifyArtifactRequest,
    db: Session = Depends(get_db),
) -> PageClassificationResponse:
    try:
        record = svc.classify_artifact(
            db, client_id, pipeline_id, body.crawl_artifact_id, body.use_llm_fallback
        )
        return PageClassificationResponse.model_validate(record)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Companies ─────────────────────────────────────────────────────────────────

@router.get(f"{_PREFIX}/extraction/companies", response_model=list[ExtractedCompanyResponse])
def list_companies(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    review_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ExtractedCompanyResponse]:
    records = svc.list_companies(db, client_id, pipeline_id, review_status)
    return [ExtractedCompanyResponse.model_validate(r) for r in records]


@router.get(
    f"{_PREFIX}/extraction/companies/{{company_id}}",
    response_model=ExtractedCompanyResponse,
)
def get_company(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ExtractedCompanyResponse:
    record = svc.get_company(db, client_id, pipeline_id, company_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return ExtractedCompanyResponse.model_validate(record)


@router.post(
    f"{_PREFIX}/extraction/extract-companies",
    response_model=list[ExtractedCompanyResponse],
    status_code=201,
)
def extract_companies(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: ExtractCompaniesRequest,
    db: Session = Depends(get_db),
) -> list[ExtractedCompanyResponse]:
    try:
        records = svc.extract_companies(
            db, client_id, pipeline_id, body.crawl_artifact_id, body.use_llm_fallback
        )
        return [ExtractedCompanyResponse.model_validate(r) for r in records]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Signals ───────────────────────────────────────────────────────────────────

@router.get(f"{_PREFIX}/extraction/signals", response_model=list[ExtractedSignalResponse])
def list_signals(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ExtractedSignalResponse]:
    records = svc.list_signals(db, client_id, pipeline_id, company_id)
    return [ExtractedSignalResponse.model_validate(r) for r in records]


@router.post(
    f"{_PREFIX}/extraction/extract-signals",
    response_model=list[ExtractedSignalResponse],
    status_code=201,
)
def extract_signals(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: ExtractSignalsRequest,
    db: Session = Depends(get_db),
) -> list[ExtractedSignalResponse]:
    try:
        records = svc.extract_signals(
            db, client_id, pipeline_id, body.crawl_artifact_id,
            body.extracted_company_id, body.use_llm_fallback,
        )
        return [ExtractedSignalResponse.model_validate(r) for r in records]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Contacts ──────────────────────────────────────────────────────────────────

@router.get(f"{_PREFIX}/extraction/contacts", response_model=list[ExtractedContactResponse])
def list_contacts(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ExtractedContactResponse]:
    records = svc.list_contacts(db, client_id, pipeline_id, company_id)
    return [ExtractedContactResponse.model_validate(r) for r in records]


@router.post(
    f"{_PREFIX}/extraction/extract-contacts",
    response_model=list[ExtractedContactResponse],
    status_code=201,
)
def extract_contacts(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: ExtractContactsRequest,
    db: Session = Depends(get_db),
) -> list[ExtractedContactResponse]:
    try:
        records = svc.extract_contacts(
            db, client_id, pipeline_id, body.crawl_artifact_id,
            body.extracted_company_id, body.use_llm_fallback,
        )
        return [ExtractedContactResponse.model_validate(r) for r in records]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Profile candidates ────────────────────────────────────────────────────────

@router.get(
    f"{_PREFIX}/extraction/profile-candidates",
    response_model=list[ProfileCandidateResponse],
)
def list_profile_candidates(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    seed_lead_row_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ProfileCandidateResponse]:
    records = svc.list_profile_candidates(db, client_id, pipeline_id, seed_lead_row_id)
    return [ProfileCandidateResponse.model_validate(r) for r in records]


@router.post(
    f"{_PREFIX}/extraction/rank-profiles",
    response_model=list[ProfileCandidateResponse],
    status_code=201,
)
def rank_profile_candidates(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: RankProfileCandidatesRequest,
    db: Session = Depends(get_db),
) -> list[ProfileCandidateResponse]:
    try:
        records = svc.rank_profile_candidates(
            db, client_id, pipeline_id, body.seed_lead_row_id
        )
        return [ProfileCandidateResponse.model_validate(r) for r in records]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Enrichment ────────────────────────────────────────────────────────────────

@router.post(f"{_PREFIX}/enrichment", response_model=EnrichmentRecordResponse, status_code=201)
def enrich_contact(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: EnrichContactRequest,
    db: Session = Depends(get_db),
) -> EnrichmentRecordResponse:
    record = svc.enrich_contact(db, client_id, pipeline_id, body)
    return EnrichmentRecordResponse.model_validate(record)


@router.get(f"{_PREFIX}/enrichment", response_model=list[EnrichmentRecordResponse])
def list_enrichment(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[EnrichmentRecordResponse]:
    records = svc.list_enrichment_records(db, client_id, pipeline_id, status)
    return [EnrichmentRecordResponse.model_validate(r) for r in records]


# ── Email verification ────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/email-verification",
    response_model=EmailVerificationResponse,
    status_code=201,
)
def verify_email(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> EmailVerificationResponse:
    record = svc.verify_email(db, client_id, pipeline_id, body)
    return EmailVerificationResponse.model_validate(record)


@router.get(
    f"{_PREFIX}/email-verification",
    response_model=list[EmailVerificationResponse],
)
def list_verification(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[EmailVerificationResponse]:
    records = svc.list_verification_records(db, client_id, pipeline_id, status)
    return [EmailVerificationResponse.model_validate(r) for r in records]


# ── Research summaries ────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/research-summaries",
    response_model=ResearchSummaryResponse,
    status_code=201,
)
def generate_summary(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    body: GenerateSummaryRequest,
    db: Session = Depends(get_db),
) -> ResearchSummaryResponse:
    try:
        record = svc.generate_summary(db, client_id, pipeline_id, body)
        return ResearchSummaryResponse.model_validate(record)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(f"{_PREFIX}/research-summaries", response_model=list[ResearchSummaryResponse])
def list_summaries(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    company_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ResearchSummaryResponse]:
    records = svc.list_summaries(db, client_id, pipeline_id, company_id)
    return [ResearchSummaryResponse.model_validate(r) for r in records]
