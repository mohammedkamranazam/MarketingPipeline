"""
Tests for crawl_service.

Acceptance criteria tested:
- create_crawl_job persists job scoped to client/pipeline with generated idempotency_key.
- list_crawl_jobs filters by status.
- get_crawl_job returns None for cross-pipeline access.
- update_crawl_job applies partial update; raises ValueError when not found.
- cancel_crawl_job sets status=cancelled; returns False for terminal jobs.
- cancel_crawl_job returns False for cross-pipeline job.
- store_artifact persists artifact with content_hash.
- store_artifact is idempotent by (pipeline_id, content_hash).
- list_artifacts filters by artifact_type.
- get_artifact returns None for cross-pipeline access.
- check_robots allows normal paths; disallows /private/ paths.
- acquire_budget raises ValueError when budget exhausted.
- release_budget decrements current_count (floor at 0).
- run_crawl_job executes crawl, stores artifact, marks job completed.
- run_crawl_job marks job blocked when robots disallows.
- run_crawl_job raises ValueError for missing job.
- Pipeline isolation: jobs and artifacts do not leak across pipelines.
- MockCrawlAdapter: certified, fetch returns content, robots returns txt.
- MockCrawlAdapter: unknown operation returns failure.
"""

import uuid

import pytest

from core.adapters.base import AdapterInput
from core.adapters.mock_crawl import MockCrawlAdapter
from core.adapters.registry import ADAPTER_REGISTRY
from core.contracts.crawl import (
    ArtifactStoreRequest,
    CrawlBudgetCreate,
    CrawlJobCreate,
    CrawlJobUpdate,
)
from core.models.client import Client
from core.models.pipeline import Pipeline
from core.services import crawl_service


def _make_client(db) -> Client:
    c = Client(name=f"C-{uuid.uuid4()}", slug=f"c-{uuid.uuid4()}", status="active")
    db.add(c)
    db.flush()
    return c


def _make_pipeline(db, client_id: uuid.UUID) -> Pipeline:
    p = Pipeline(
        client_id=client_id,
        name=f"P-{uuid.uuid4()}",
        slug=f"p-{uuid.uuid4()}",
        lane="discovery",
        status="active",
    )
    db.add(p)
    db.flush()
    return p


def _job_payload(**kw) -> CrawlJobCreate:
    defaults: dict = {}
    defaults.update(kw)
    return CrawlJobCreate(**defaults)


def _artifact_payload(**kw) -> ArtifactStoreRequest:
    defaults = dict(content="<html>page</html>", artifact_type="html_page")
    defaults.update(kw)
    return ArtifactStoreRequest(**defaults)


# ── CrawlJob ──────────────────────────────────────────────────────────────────

def test_create_crawl_job(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    assert job.pipeline_id == p.id
    assert job.status == "queued"
    assert job.idempotency_key.startswith("crawl:")


def test_list_crawl_jobs_status_filter(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    j1 = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    crawl_service.update_crawl_job(
        db, c.id, p.id, j1.id, CrawlJobUpdate(status="completed")
    )
    crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    queued = crawl_service.list_crawl_jobs(db, c.id, p.id, status="queued")
    completed = crawl_service.list_crawl_jobs(db, c.id, p.id, status="completed")
    assert len(queued) == 1
    assert len(completed) == 1


def test_get_crawl_job_cross_pipeline_none(db):
    c = _make_client(db)
    p_a = _make_pipeline(db, c.id)
    p_b = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p_a.id, _job_payload())
    assert crawl_service.get_crawl_job(db, c.id, p_b.id, job.id) is None


def test_update_crawl_job(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    updated = crawl_service.update_crawl_job(
        db, c.id, p.id, job.id, CrawlJobUpdate(status="running", trace_id="t-123")
    )
    assert updated.status == "running"
    assert updated.trace_id == "t-123"


def test_update_crawl_job_not_found_raises(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    with pytest.raises(ValueError, match="not found"):
        crawl_service.update_crawl_job(
            db, c.id, p.id, uuid.uuid4(), CrawlJobUpdate(status="running")
        )


def test_cancel_crawl_job(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    assert crawl_service.cancel_crawl_job(db, c.id, p.id, job.id) is True
    refreshed = crawl_service.get_crawl_job(db, c.id, p.id, job.id)
    assert refreshed is not None
    assert refreshed.status == "cancelled"


def test_cancel_crawl_job_terminal_returns_false(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    crawl_service.update_crawl_job(db, c.id, p.id, job.id, CrawlJobUpdate(status="completed"))
    assert crawl_service.cancel_crawl_job(db, c.id, p.id, job.id) is False


def test_cancel_crawl_job_cross_pipeline_false(db):
    c = _make_client(db)
    p_a = _make_pipeline(db, c.id)
    p_b = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p_a.id, _job_payload())
    assert crawl_service.cancel_crawl_job(db, c.id, p_b.id, job.id) is False


# ── CrawlArtifact ─────────────────────────────────────────────────────────────

def test_store_artifact(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    a = crawl_service.store_artifact(db, c.id, p.id, _artifact_payload())
    assert a.pipeline_id == p.id
    assert a.content_hash is not None
    assert a.storage_key.startswith(f"artifacts/{p.id}/")


def test_store_artifact_idempotent(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    payload = _artifact_payload(content="<html>same</html>")
    a1 = crawl_service.store_artifact(db, c.id, p.id, payload)
    a2 = crawl_service.store_artifact(db, c.id, p.id, payload)
    assert a1.id == a2.id
    assert len(crawl_service.list_artifacts(db, c.id, p.id)) == 1


def test_list_artifacts_type_filter(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    crawl_service.store_artifact(
        db, c.id, p.id, _artifact_payload(content="html", artifact_type="html_page")
    )
    crawl_service.store_artifact(
        db, c.id, p.id,
        _artifact_payload(content="search", artifact_type="search_result")
    )
    html = crawl_service.list_artifacts(db, c.id, p.id, artifact_type="html_page")
    search = crawl_service.list_artifacts(db, c.id, p.id, artifact_type="search_result")
    assert len(html) == 1
    assert len(search) == 1


def test_get_artifact_cross_pipeline_none(db):
    c = _make_client(db)
    p_a = _make_pipeline(db, c.id)
    p_b = _make_pipeline(db, c.id)
    a = crawl_service.store_artifact(db, c.id, p_a.id, _artifact_payload())
    assert crawl_service.get_artifact(db, c.id, p_b.id, a.id) is None


# ── Robots check ──────────────────────────────────────────────────────────────

def test_check_robots_allows_normal(db):
    result = crawl_service.check_robots("https://example.com/page")
    assert result.allowed is True
    assert result.reason is None


def test_check_robots_disallows_private(db):
    result = crawl_service.check_robots("https://example.com/private/data")
    assert result.allowed is False
    assert result.reason is not None


# ── Concurrency budgets ───────────────────────────────────────────────────────

def test_acquire_and_release_budget(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    crawl_service.create_budget(
        db, c.id,
        CrawlBudgetCreate(pipeline_id=p.id, budget_type="pipeline", max_concurrent=2)
    )
    crawl_service.acquire_budget(db, c.id, "pipeline", pipeline_id=p.id)
    budget = crawl_service.get_budget(db, c.id, "pipeline", pipeline_id=p.id)
    assert budget is not None and budget.current_count == 1
    crawl_service.release_budget(db, c.id, "pipeline", pipeline_id=p.id)
    budget = crawl_service.get_budget(db, c.id, "pipeline", pipeline_id=p.id)
    assert budget is not None and budget.current_count == 0


def test_acquire_budget_exhausted_raises(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    crawl_service.create_budget(
        db, c.id,
        CrawlBudgetCreate(pipeline_id=p.id, budget_type="pipeline", max_concurrent=1)
    )
    crawl_service.acquire_budget(db, c.id, "pipeline", pipeline_id=p.id)
    with pytest.raises(ValueError, match="exhausted"):
        crawl_service.acquire_budget(db, c.id, "pipeline", pipeline_id=p.id)


def test_release_budget_floors_at_zero(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    crawl_service.create_budget(
        db, c.id,
        CrawlBudgetCreate(pipeline_id=p.id, budget_type="pipeline", max_concurrent=2)
    )
    crawl_service.release_budget(db, c.id, "pipeline", pipeline_id=p.id)
    budget = crawl_service.get_budget(db, c.id, "pipeline", pipeline_id=p.id)
    assert budget is not None and budget.current_count == 0


def test_acquire_no_budget_allows(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    # No budget configured — should not raise
    crawl_service.acquire_budget(db, c.id, "pipeline", pipeline_id=p.id)


# ── run_crawl_job ─────────────────────────────────────────────────────────────

def test_run_crawl_job_success(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    artifact = crawl_service.run_crawl_job(
        db, c.id, p.id, job.id, "https://example.com/page"
    )
    assert artifact.pipeline_id == p.id
    assert artifact.artifact_type == "html_page"
    refreshed = crawl_service.get_crawl_job(db, c.id, p.id, job.id)
    assert refreshed is not None and refreshed.status == "completed"


def test_run_crawl_job_robots_blocks(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    job = crawl_service.create_crawl_job(db, c.id, p.id, _job_payload())
    with pytest.raises(ValueError, match="blocked"):
        crawl_service.run_crawl_job(
            db, c.id, p.id, job.id, "https://example.com/private/data"
        )
    blocked = crawl_service.get_crawl_job(db, c.id, p.id, job.id)
    assert blocked is not None and blocked.status == "blocked"


def test_run_crawl_job_not_found_raises(db):
    c = _make_client(db)
    p = _make_pipeline(db, c.id)
    with pytest.raises(ValueError, match="not found"):
        crawl_service.run_crawl_job(db, c.id, p.id, uuid.uuid4(), "https://example.com")


# ── MockCrawlAdapter certification ────────────────────────────────────────────

def test_mock_crawl_adapter_in_registry():
    assert "mock_crawl" in ADAPTER_REGISTRY


def test_mock_crawl_adapter_certified():
    assert MockCrawlAdapter.META.is_certified is True
    assert MockCrawlAdapter.META.source_type == "public_web"


def test_mock_crawl_fetch_returns_content():
    adapter = MockCrawlAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="fetch", payload={"url": "https://example.com/about"}
    ))
    assert result.success is True
    data = result.data_dict()
    assert "content" in data
    assert "content_hash" in data
    assert data["status_code"] == 200


def test_mock_crawl_robots_returns_txt():
    adapter = MockCrawlAdapter()
    result = adapter.execute(AdapterInput(
        operation_type="robots", payload={"url": "https://example.com"}
    ))
    assert result.success is True
    data = result.data_dict()
    assert "content" in data
    assert "User-agent" in data["content"]


def test_mock_crawl_unknown_operation_returns_failure():
    adapter = MockCrawlAdapter()
    result = adapter.execute(AdapterInput(operation_type="screenshot", payload={}))
    assert result.success is False
    assert "does not support" in (result.error or "")


def test_mock_crawl_deterministic_hash():
    adapter = MockCrawlAdapter()
    r1 = adapter.execute(AdapterInput(operation_type="fetch", payload={"url": "https://x.com"}))
    r2 = adapter.execute(AdapterInput(operation_type="fetch", payload={"url": "https://x.com"}))
    assert r1.data_dict()["content_hash"] == r2.data_dict()["content_hash"]


# ── Pipeline isolation ────────────────────────────────────────────────────────

def test_crawl_jobs_pipeline_isolation(db):
    c = _make_client(db)
    p_a = _make_pipeline(db, c.id)
    p_b = _make_pipeline(db, c.id)
    crawl_service.create_crawl_job(db, c.id, p_a.id, _job_payload())
    assert crawl_service.list_crawl_jobs(db, c.id, p_b.id) == []


def test_artifacts_pipeline_isolation(db):
    c = _make_client(db)
    p_a = _make_pipeline(db, c.id)
    p_b = _make_pipeline(db, c.id)
    crawl_service.store_artifact(db, c.id, p_a.id, _artifact_payload())
    assert crawl_service.list_artifacts(db, c.id, p_b.id) == []
