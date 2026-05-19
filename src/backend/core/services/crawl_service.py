"""
Acceptance Criteria:
- create_crawl_job persists CrawlJob scoped to client/pipeline; generates idempotency_key.
- list_crawl_jobs returns jobs for the pipeline, optional status filter.
- get_crawl_job returns None when not found or wrong pipeline.
- update_crawl_job applies partial update; raises ValueError when not found.
- cancel_crawl_job sets status=cancelled; returns False when not found or already terminal.
- store_artifact persists CrawlArtifact; deduplicates by (pipeline_id, content_hash).
- list_artifacts returns artifacts for the pipeline, optional artifact_type filter.
- get_artifact returns None when not found or wrong pipeline.
- check_robots(url) returns RobotsCheckResult using mock adapter; disallows /private/ paths.
- check_rate_limit(pipeline_id, connector_id) raises ValueError when budget is exhausted.
- acquire_budget(client_id, pipeline_id, budget_type, source_connector_id?) creates/increments.
- release_budget(client_id, pipeline_id, budget_type, source_connector_id?) decrements.
- run_crawl_job executes crawl via adapter; stores artifact; marks job completed or failed.
- get_budget(client_id, budget_type) returns budget or None.
- list_budgets(client_id, pipeline_id) returns all budgets for pipeline.
- All records scoped by client_id and pipeline_id.
"""

import hashlib
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.adapters.base import AdapterInput
from core.adapters.mock_crawl import MockCrawlAdapter
from core.contracts.crawl import (
    ArtifactStoreRequest,
    CrawlBudgetCreate,
    CrawlJobCreate,
    CrawlJobUpdate,
    RobotsCheckResult,
)
from core.models.crawl import CrawlArtifact, CrawlBudget, CrawlJob


def _utcnow() -> datetime:
    return datetime.now(UTC)


_TERMINAL_STATUSES = {"completed", "failed", "cancelled", "blocked"}

_mock_crawl_adapter = MockCrawlAdapter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def _make_storage_key(
    pipeline_id: uuid.UUID,
    artifact_type: str,
    artifact_id: uuid.UUID,
) -> str:
    return f"artifacts/{pipeline_id}/{artifact_type}/{artifact_id}"


# ── CrawlJob ──────────────────────────────────────────────────────────────────

def create_crawl_job(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: CrawlJobCreate,
) -> CrawlJob:
    idempotency_key = f"crawl:{pipeline_id}:{uuid.uuid4()}"
    job = CrawlJob(
        client_id=client_id,
        pipeline_id=pipeline_id,
        source_connector_id=payload.source_connector_id,
        job_type=payload.job_type,
        status="queued",
        idempotency_key=idempotency_key,
        trigger=payload.trigger,
        max_attempts=payload.max_attempts,
        scheduled_at=_utcnow(),
        rate_limit_per_minute=payload.rate_limit_per_minute,
        robots_txt_url=payload.robots_txt_url,
        concurrency_budget=payload.concurrency_budget,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_crawl_jobs(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = None,
) -> list[CrawlJob]:
    stmt = select(CrawlJob).where(
        CrawlJob.client_id == client_id,
        CrawlJob.pipeline_id == pipeline_id,
    )
    if status:
        stmt = stmt.where(CrawlJob.status == status)
    stmt = stmt.order_by(CrawlJob.scheduled_at.desc())
    return list(db.scalars(stmt).all())


def get_crawl_job(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
) -> CrawlJob | None:
    job = db.get(CrawlJob, job_id)
    if job is None or job.client_id != client_id or job.pipeline_id != pipeline_id:
        return None
    return job


def update_crawl_job(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
    payload: CrawlJobUpdate,
) -> CrawlJob:
    job = get_crawl_job(db, client_id, pipeline_id, job_id)
    if job is None:
        raise ValueError(f"CrawlJob {job_id} not found")
    if payload.status is not None:
        job.status = payload.status
    if payload.error_code is not None:
        job.error_code = payload.error_code
    if payload.error_message is not None:
        job.error_message = payload.error_message
    if payload.trace_id is not None:
        job.trace_id = payload.trace_id
    if payload.started_at is not None:
        job.started_at = payload.started_at
    if payload.finished_at is not None:
        job.finished_at = payload.finished_at
    db.commit()
    db.refresh(job)
    return job


def cancel_crawl_job(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
) -> bool:
    job = get_crawl_job(db, client_id, pipeline_id, job_id)
    if job is None or job.status in _TERMINAL_STATUSES:
        return False
    job.status = "cancelled"
    job.finished_at = _utcnow()
    db.commit()
    return True


# ── CrawlArtifact ─────────────────────────────────────────────────────────────

def store_artifact(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    request: ArtifactStoreRequest,
) -> CrawlArtifact:
    content_hash = _content_hash(request.content)

    # Idempotency: return existing artifact if same content already stored in pipeline
    existing_stmt = select(CrawlArtifact).where(
        CrawlArtifact.pipeline_id == pipeline_id,
        CrawlArtifact.content_hash == content_hash,
    )
    existing = db.scalars(existing_stmt).first()
    if existing is not None:
        return existing

    artifact_id = uuid.uuid4()
    storage_key = _make_storage_key(pipeline_id, request.artifact_type, artifact_id)

    artifact = CrawlArtifact(
        id=artifact_id,
        client_id=client_id,
        pipeline_id=pipeline_id,
        crawl_job_id=request.crawl_job_id,
        source_connector_id=request.source_connector_id,
        seed_lead_row_id=request.seed_lead_row_id,
        artifact_type=request.artifact_type,
        url=request.url,
        storage_key=storage_key,
        content_hash=content_hash,
        status="stored",
        policy_decision=request.policy_decision,
        mime_type=request.mime_type,
        size_bytes=len(request.content.encode()),
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def list_artifacts(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_type: str | None = None,
) -> list[CrawlArtifact]:
    stmt = select(CrawlArtifact).where(
        CrawlArtifact.client_id == client_id,
        CrawlArtifact.pipeline_id == pipeline_id,
    )
    if artifact_type:
        stmt = stmt.where(CrawlArtifact.artifact_type == artifact_type)
    stmt = stmt.order_by(CrawlArtifact.created_at.desc())
    return list(db.scalars(stmt).all())


def get_artifact(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    artifact_id: uuid.UUID,
) -> CrawlArtifact | None:
    a = db.get(CrawlArtifact, artifact_id)
    if a is None or a.client_id != client_id or a.pipeline_id != pipeline_id:
        return None
    return a


# ── Robots check ──────────────────────────────────────────────────────────────

def check_robots(url: str) -> RobotsCheckResult:
    """Mock robots check: disallows /private/ paths."""
    from urllib.parse import urlparse
    path = urlparse(url).path
    if path.startswith("/private"):
        return RobotsCheckResult(url=url, allowed=False, reason="Path disallowed by robots.txt")
    return RobotsCheckResult(url=url, allowed=True)


# ── Concurrency budgets ───────────────────────────────────────────────────────

def get_budget(
    db: Session,
    client_id: uuid.UUID,
    budget_type: str,
    pipeline_id: uuid.UUID | None = None,
    source_connector_id: uuid.UUID | None = None,
) -> CrawlBudget | None:
    stmt = select(CrawlBudget).where(
        CrawlBudget.client_id == client_id,
        CrawlBudget.budget_type == budget_type,
        CrawlBudget.pipeline_id == pipeline_id,
        CrawlBudget.source_connector_id == source_connector_id,
    )
    return db.scalars(stmt).first()


def list_budgets(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[CrawlBudget]:
    stmt = select(CrawlBudget).where(
        CrawlBudget.client_id == client_id,
        CrawlBudget.pipeline_id == pipeline_id,
    )
    return list(db.scalars(stmt).all())


def create_budget(
    db: Session,
    client_id: uuid.UUID,
    payload: CrawlBudgetCreate,
) -> CrawlBudget:
    budget = CrawlBudget(
        client_id=client_id,
        pipeline_id=payload.pipeline_id,
        source_connector_id=payload.source_connector_id,
        adapter_key=payload.adapter_key,
        budget_type=payload.budget_type,
        max_concurrent=payload.max_concurrent,
        current_count=0,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def acquire_budget(
    db: Session,
    client_id: uuid.UUID,
    budget_type: str,
    pipeline_id: uuid.UUID | None = None,
    source_connector_id: uuid.UUID | None = None,
) -> None:
    """Increment current_count; raises ValueError if budget is exhausted."""
    budget = get_budget(db, client_id, budget_type, pipeline_id, source_connector_id)
    if budget is None:
        return  # No budget configured — allow by default
    if budget.current_count >= budget.max_concurrent:
        raise ValueError(
            f"Concurrency budget exhausted for type='{budget_type}' "
            f"(max={budget.max_concurrent}, current={budget.current_count})"
        )
    budget.current_count += 1
    db.commit()


def release_budget(
    db: Session,
    client_id: uuid.UUID,
    budget_type: str,
    pipeline_id: uuid.UUID | None = None,
    source_connector_id: uuid.UUID | None = None,
) -> None:
    """Decrement current_count (floor at 0)."""
    budget = get_budget(db, client_id, budget_type, pipeline_id, source_connector_id)
    if budget is None:
        return
    budget.current_count = max(0, budget.current_count - 1)
    db.commit()


# ── High-level crawl execution ────────────────────────────────────────────────

def run_crawl_job(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    job_id: uuid.UUID,
    url: str,
    policy_decision: str | None = None,
) -> CrawlArtifact:
    """
    Execute a crawl job via MockCrawlAdapter, store the artifact, and mark the job done.
    Raises ValueError if job not found or if robots check blocks the URL.
    """
    job = get_crawl_job(db, client_id, pipeline_id, job_id)
    if job is None:
        raise ValueError(f"CrawlJob {job_id} not found")

    robots = check_robots(url)
    if not robots.allowed:
        job.status = "blocked"
        job.error_message = robots.reason
        job.finished_at = _utcnow()
        db.commit()
        raise ValueError(f"URL blocked by robots: {robots.reason}")

    job.status = "running"
    job.started_at = _utcnow()
    job.attempt += 1
    db.commit()

    try:
        result = _mock_crawl_adapter.execute(
            AdapterInput(operation_type="fetch", payload={"url": url})
        )
        if not result.success:
            job.status = "failed"
            job.error_message = result.error
            job.finished_at = _utcnow()
            db.commit()
            raise ValueError(f"Crawl failed: {result.error}")

        data = result.data_dict()
        artifact = store_artifact(
            db,
            client_id,
            pipeline_id,
            ArtifactStoreRequest(
                url=url,
                content=data.get("content", ""),
                mime_type=data.get("mime_type", "text/html"),
                artifact_type="html_page",
                policy_decision=policy_decision,
                crawl_job_id=job_id,
                source_connector_id=job.source_connector_id,
            ),
        )

        job.status = "completed"
        job.finished_at = _utcnow()
        db.commit()
        return artifact

    except ValueError:
        raise
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = _utcnow()
        db.commit()
        raise ValueError(f"Crawl execution error: {exc}") from exc
