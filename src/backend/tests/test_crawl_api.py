"""
Tests for crawl API routes.

Acceptance criteria tested:
- POST /crawl-jobs returns 201 with CrawlJobResponse.
- GET /crawl-jobs returns list; ?status= filter works.
- GET /crawl-jobs/{job_id} returns 404 when not found.
- PATCH /crawl-jobs/{job_id} returns 422 for unknown job.
- POST /crawl-jobs/{job_id}/cancel returns 204; 404 for unknown.
- POST /crawl-jobs/{job_id}/run returns CrawlArtifactResponse; 422 for blocked URL.
- POST /artifacts returns 201.
- GET /artifacts returns list; ?artifact_type= filter works.
- GET /artifacts/{artifact_id} returns 404 for unknown.
- POST /robots-check returns RobotsCheckResult.
- GET /budgets returns list.
- POST /clients/{cid}/budgets returns 201.
- Pipeline isolation for crawl jobs and artifacts.
"""

import uuid


def _create_client(api_client) -> dict:
    r = api_client.post(
        "/clients",
        json={"name": f"C-{uuid.uuid4()}", "slug": f"c-{uuid.uuid4()}", "status": "active"},
    )
    assert r.status_code == 201
    return r.json()


def _create_pipeline(api_client, client_id: str) -> dict:
    r = api_client.post(
        f"/clients/{client_id}/pipelines",
        json={
            "name": f"P-{uuid.uuid4()}",
            "slug": f"p-{uuid.uuid4()}",
            "lane": "discovery",
            "status": "active",
        },
    )
    assert r.status_code == 201
    return r.json()


def _base(cid: str, pid: str) -> str:
    return f"/clients/{cid}/pipelines/{pid}"


# ── CrawlJob ──────────────────────────────────────────────────────────────────

def test_create_crawl_job_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={})
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "queued"
    assert data["pipeline_id"] == p["id"]


def test_list_crawl_jobs(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={})
    api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={})
    r = api_client.get(f"{_base(c['id'], p['id'])}/crawl-jobs")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_crawl_jobs_status_filter(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    created = api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={}).json()
    api_client.patch(
        f"{_base(c['id'], p['id'])}/crawl-jobs/{created['id']}",
        json={"status": "completed"},
    )
    api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={})
    queued = api_client.get(
        f"{_base(c['id'], p['id'])}/crawl-jobs", params={"status": "queued"}
    )
    assert len(queued.json()) == 1


def test_get_crawl_job_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.get(f"{_base(c['id'], p['id'])}/crawl-jobs/{uuid.uuid4()}")
    assert r.status_code == 404


def test_update_crawl_job_422_not_found(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.patch(
        f"{_base(c['id'], p['id'])}/crawl-jobs/{uuid.uuid4()}",
        json={"status": "running"},
    )
    assert r.status_code == 422


def test_cancel_crawl_job_204(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    created = api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={}).json()
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/crawl-jobs/{created['id']}/cancel"
    )
    assert r.status_code == 204


def test_cancel_crawl_job_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/crawl-jobs/{uuid.uuid4()}/cancel"
    )
    assert r.status_code == 404


def test_run_crawl_job_success(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    created = api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={}).json()
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/crawl-jobs/{created['id']}/run",
        params={"url": "https://example.com/page"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["artifact_type"] == "html_page"
    assert data["pipeline_id"] == p["id"]


def test_run_crawl_job_blocked_422(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    created = api_client.post(f"{_base(c['id'], p['id'])}/crawl-jobs", json={}).json()
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/crawl-jobs/{created['id']}/run",
        params={"url": "https://example.com/private/secret"},
    )
    assert r.status_code == 422


# ── CrawlArtifact ─────────────────────────────────────────────────────────────

def test_store_artifact_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/artifacts",
        json={"content": "<html>hi</html>", "artifact_type": "html_page"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["pipeline_id"] == p["id"]
    assert data["content_hash"] is not None


def test_list_artifacts(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.post(
        f"{_base(c['id'], p['id'])}/artifacts",
        json={"content": "a", "artifact_type": "html_page"},
    )
    api_client.post(
        f"{_base(c['id'], p['id'])}/artifacts",
        json={"content": "b", "artifact_type": "search_result"},
    )
    r = api_client.get(f"{_base(c['id'], p['id'])}/artifacts")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_artifacts_type_filter(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    api_client.post(
        f"{_base(c['id'], p['id'])}/artifacts",
        json={"content": "html-content", "artifact_type": "html_page"},
    )
    r = api_client.get(
        f"{_base(c['id'], p['id'])}/artifacts",
        params={"artifact_type": "html_page"},
    )
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["artifact_type"] == "html_page"


def test_get_artifact_404(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.get(f"{_base(c['id'], p['id'])}/artifacts/{uuid.uuid4()}")
    assert r.status_code == 404


# ── Robots check ──────────────────────────────────────────────────────────────

def test_robots_check_allowed(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/robots-check",
        params={"url": "https://example.com/page"},
    )
    assert r.status_code == 200
    assert r.json()["allowed"] is True


def test_robots_check_disallowed(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(
        f"{_base(c['id'], p['id'])}/robots-check",
        params={"url": "https://example.com/private/stuff"},
    )
    assert r.status_code == 200
    assert r.json()["allowed"] is False


# ── Budgets ───────────────────────────────────────────────────────────────────

def test_list_budgets_empty(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.get(f"{_base(c['id'], p['id'])}/budgets")
    assert r.status_code == 200
    assert r.json() == []


def test_create_budget_201(api_client):
    c = _create_client(api_client)
    p = _create_pipeline(api_client, c["id"])
    r = api_client.post(
        f"/clients/{c['id']}/budgets",
        json={"pipeline_id": p["id"], "budget_type": "pipeline", "max_concurrent": 3},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["max_concurrent"] == 3
    assert data["budget_type"] == "pipeline"


# ── Pipeline isolation ────────────────────────────────────────────────────────

def test_crawl_jobs_pipeline_isolation(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(f"{_base(c['id'], p_a['id'])}/crawl-jobs", json={})
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/crawl-jobs")
    assert r.status_code == 200
    assert r.json() == []


def test_artifacts_pipeline_isolation(api_client):
    c = _create_client(api_client)
    p_a = _create_pipeline(api_client, c["id"])
    p_b = _create_pipeline(api_client, c["id"])
    api_client.post(
        f"{_base(c['id'], p_a['id'])}/artifacts",
        json={"content": "page content", "artifact_type": "html_page"},
    )
    r = api_client.get(f"{_base(c['id'], p_b['id'])}/artifacts")
    assert r.status_code == 200
    assert r.json() == []
