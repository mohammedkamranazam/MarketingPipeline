"""
Acceptance Criteria:
- POST /clients/{cid}/pipelines/{pid}/crawl-jobs creates a crawl job (201).
- GET /clients/{cid}/pipelines/{pid}/crawl-jobs lists jobs; optional ?status= filter.
- GET /clients/{cid}/pipelines/{pid}/crawl-jobs/{job_id} returns job or 404.
- PATCH /clients/{cid}/pipelines/{pid}/crawl-jobs/{job_id} updates job or 422.
- POST /clients/{cid}/pipelines/{pid}/crawl-jobs/{job_id}/cancel cancels job or 404.
- POST /clients/{cid}/pipelines/{pid}/crawl-jobs/{job_id}/run executes crawl and returns artifact.
- POST /clients/{cid}/pipelines/{pid}/artifacts stores artifact (201 or 200 if deduped).
- GET /clients/{cid}/pipelines/{pid}/artifacts lists artifacts; optional ?artifact_type= filter.
- GET /clients/{cid}/pipelines/{pid}/artifacts/{artifact_id} returns artifact or 404.
- POST /clients/{cid}/pipelines/{pid}/robots-check returns RobotsCheckResult.
- GET /clients/{cid}/pipelines/{pid}/budgets lists budgets for pipeline.
- POST /clients/{cid}/budgets creates a budget.
- All routes delegate to crawl_service; routes handle HTTP only.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.contracts.crawl import (
    ArtifactStoreRequest,
    CrawlArtifactResponse,
    CrawlBudgetCreate,
    CrawlBudgetResponse,
    CrawlJobCreate,
    CrawlJobResponse,
    CrawlJobUpdate,
    RobotsCheckResult,
)
from core.db.session import get_db
from core.services import crawl_service

_PREFIX = "/clients/{client_id}/pipelines/{pipeline_id}"
router = APIRouter(tags=["crawl"])


# ── CrawlJob ──────────────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/crawl-jobs",
    response_model=CrawlJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_crawl_job(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: CrawlJobCreate,
    db: Session = Depends(get_db),
) -> CrawlJobResponse:
    job = crawl_service.create_crawl_job(db, client_id, pipeline_id, payload)
    return CrawlJobResponse.model_validate(job)


@router.get(f"{_PREFIX}/crawl-jobs", response_model=list[CrawlJobResponse])
def list_crawl_jobs(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[CrawlJobResponse]:
    jobs = crawl_service.list_crawl_jobs(db, client_id, pipeline_id, status_filter)
    return [CrawlJobResponse.model_validate(j) for j in jobs]


@router.get(
    f"{_PREFIX}/crawl-jobs/{{job_id}}", response_model=CrawlJobResponse
)
def get_crawl_job(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CrawlJobResponse:
    job = crawl_service.get_crawl_job(db, client_id, pipeline_id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crawl job not found")
    return CrawlJobResponse.model_validate(job)


@router.patch(f"{_PREFIX}/crawl-jobs/{{job_id}}", response_model=CrawlJobResponse)
def update_crawl_job(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
    payload: CrawlJobUpdate,
    db: Session = Depends(get_db),
) -> CrawlJobResponse:
    try:
        job = crawl_service.update_crawl_job(db, client_id, pipeline_id, job_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return CrawlJobResponse.model_validate(job)


@router.post(
    f"{_PREFIX}/crawl-jobs/{{job_id}}/cancel",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_crawl_job(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    cancelled = crawl_service.cancel_crawl_job(db, client_id, pipeline_id, job_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found or already in terminal state",
        )


@router.post(
    f"{_PREFIX}/crawl-jobs/{{job_id}}/run",
    response_model=CrawlArtifactResponse,
)
def run_crawl_job(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
    url: str = Query(...),
    policy_decision: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> CrawlArtifactResponse:
    try:
        artifact = crawl_service.run_crawl_job(
            db, client_id, pipeline_id, job_id, url, policy_decision
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return CrawlArtifactResponse.model_validate(artifact)


# ── CrawlArtifact ─────────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/artifacts",
    response_model=CrawlArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
def store_artifact(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: ArtifactStoreRequest,
    db: Session = Depends(get_db),
) -> CrawlArtifactResponse:
    artifact = crawl_service.store_artifact(db, client_id, pipeline_id, payload)
    return CrawlArtifactResponse.model_validate(artifact)


@router.get(f"{_PREFIX}/artifacts", response_model=list[CrawlArtifactResponse])
def list_artifacts(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CrawlArtifactResponse]:
    artifacts = crawl_service.list_artifacts(db, client_id, pipeline_id, artifact_type)
    return [CrawlArtifactResponse.model_validate(a) for a in artifacts]


@router.get(
    f"{_PREFIX}/artifacts/{{artifact_id}}", response_model=CrawlArtifactResponse
)
def get_artifact(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CrawlArtifactResponse:
    a = crawl_service.get_artifact(db, client_id, pipeline_id, artifact_id)
    if a is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")
    return CrawlArtifactResponse.model_validate(a)


# ── Robots check ──────────────────────────────────────────────────────────────

@router.post(f"{_PREFIX}/robots-check", response_model=RobotsCheckResult)
def robots_check(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    url: str = Query(...),
) -> RobotsCheckResult:
    return crawl_service.check_robots(url)


# ── Budgets ───────────────────────────────────────────────────────────────────

@router.get(f"{_PREFIX}/budgets", response_model=list[CrawlBudgetResponse])
def list_budgets(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[CrawlBudgetResponse]:
    budgets = crawl_service.list_budgets(db, client_id, pipeline_id)
    return [CrawlBudgetResponse.model_validate(b) for b in budgets]


@router.post(
    "/clients/{client_id}/budgets",
    response_model=CrawlBudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    client_id: uuid.UUID,
    payload: CrawlBudgetCreate,
    db: Session = Depends(get_db),
) -> CrawlBudgetResponse:
    budget = crawl_service.create_budget(db, client_id, payload)
    return CrawlBudgetResponse.model_validate(budget)
