"""
Acceptance Criteria:
- POST /clients returns 201 with ClientResponse body.
- GET /clients returns list of clients.
- GET /clients/{id} returns 200 for existing, 404 for missing.
- PATCH /clients/{id} applies partial update.
- POST /clients/{id}/pipelines returns 201 with PipelineResponse.
- GET /clients/{id}/pipelines returns only that client's pipelines.
- GET /clients/{id}/pipelines/{pid} returns 200 or 404.
- PATCH /clients/{id}/pipelines/{pid} applies partial update.
- Two pipelines under one client are independent (isolation test).
"""

import uuid

from fastapi.testclient import TestClient


def test_create_client_returns_201(api_client: TestClient) -> None:
    resp = api_client.post("/clients", json={"name": "API Client", "slug": "api-client"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "API Client"
    assert body["slug"] == "api-client"
    assert body["status"] == "active"
    assert "id" in body


def test_list_clients_returns_list(api_client: TestClient) -> None:
    api_client.post("/clients", json={"name": "List Client A", "slug": "list-client-a"})
    api_client.post("/clients", json={"name": "List Client B", "slug": "list-client-b"})
    resp = api_client.get("/clients")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 2


def test_get_client_returns_200(api_client: TestClient) -> None:
    created = api_client.post("/clients", json={"name": "Get Me", "slug": "get-me"}).json()
    resp = api_client.get(f"/clients/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_client_missing_returns_404(api_client: TestClient) -> None:
    resp = api_client.get(f"/clients/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_patch_client_applies_changes(api_client: TestClient) -> None:
    created = api_client.post("/clients", json={"name": "Patch Me", "slug": "patch-me"}).json()
    resp = api_client.patch(f"/clients/{created['id']}", json={"status": "inactive"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"
    assert resp.json()["name"] == "Patch Me"


def test_patch_client_missing_returns_404(api_client: TestClient) -> None:
    resp = api_client.patch(f"/clients/{uuid.uuid4()}", json={"status": "inactive"})
    assert resp.status_code == 404


def _create_client(api_client: TestClient, name: str, slug: str) -> dict:
    return api_client.post("/clients", json={"name": name, "slug": slug}).json()


def test_create_pipeline_returns_201(api_client: TestClient) -> None:
    client = _create_client(api_client, "Pipeline Owner", "pipeline-owner")
    resp = api_client.post(
        f"/clients/{client['id']}/pipelines",
        json={"name": "Discovery", "slug": "discovery", "lane": "discovery"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["client_id"] == client["id"]
    assert body["lane"] == "discovery"


def test_create_pipeline_for_missing_client_returns_404(api_client: TestClient) -> None:
    resp = api_client.post(
        f"/clients/{uuid.uuid4()}/pipelines",
        json={"name": "Orphan", "slug": "orphan", "lane": "discovery"},
    )
    assert resp.status_code == 404


def test_list_pipelines_isolated_per_client(api_client: TestClient) -> None:
    c1 = _create_client(api_client, "Iso Client 1", "iso-client-1")
    c2 = _create_client(api_client, "Iso Client 2", "iso-client-2")

    api_client.post(
        f"/clients/{c1['id']}/pipelines", json={"name": "P1", "slug": "p1", "lane": "discovery"}
    )
    api_client.post(
        f"/clients/{c1['id']}/pipelines",
        json={"name": "P2", "slug": "p2", "lane": "seed_enrichment"},
    )
    api_client.post(
        f"/clients/{c2['id']}/pipelines", json={"name": "P3", "slug": "p3", "lane": "discovery"}
    )

    r1 = api_client.get(f"/clients/{c1['id']}/pipelines")
    r2 = api_client.get(f"/clients/{c2['id']}/pipelines")

    assert len(r1.json()) == 2
    assert len(r2.json()) == 1
    assert all(p["client_id"] == c1["id"] for p in r1.json())
    assert all(p["client_id"] == c2["id"] for p in r2.json())


def test_get_pipeline_returns_200(api_client: TestClient) -> None:
    client = _create_client(api_client, "Get Pipeline Owner", "get-pipeline-owner")
    pipeline = api_client.post(
        f"/clients/{client['id']}/pipelines",
        json={"name": "Fetch Me", "slug": "fetch-me", "lane": "discovery"},
    ).json()
    resp = api_client.get(f"/clients/{client['id']}/pipelines/{pipeline['id']}")
    assert resp.status_code == 200


def test_get_pipeline_missing_returns_404(api_client: TestClient) -> None:
    client = _create_client(api_client, "Empty Owner", "empty-owner")
    resp = api_client.get(f"/clients/{client['id']}/pipelines/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_patch_pipeline_applies_changes(api_client: TestClient) -> None:
    client = _create_client(api_client, "Patch Pipeline Owner", "patch-pipeline-owner")
    pipeline = api_client.post(
        f"/clients/{client['id']}/pipelines",
        json={"name": "Before", "slug": "before", "lane": "discovery"},
    ).json()
    resp = api_client.patch(
        f"/clients/{client['id']}/pipelines/{pipeline['id']}",
        json={"status": "paused"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "paused"
    assert resp.json()["name"] == "Before"


def test_two_pipelines_under_one_client_are_independent(api_client: TestClient) -> None:
    client = _create_client(api_client, "Dual Pipeline", "dual-pipeline")
    p1 = api_client.post(
        f"/clients/{client['id']}/pipelines",
        json={"name": "Alpha", "slug": "alpha", "lane": "discovery"},
    ).json()
    p2 = api_client.post(
        f"/clients/{client['id']}/pipelines",
        json={"name": "Beta", "slug": "beta", "lane": "seed_enrichment"},
    ).json()

    api_client.patch(f"/clients/{client['id']}/pipelines/{p1['id']}", json={"status": "paused"})

    p1_fresh = api_client.get(f"/clients/{client['id']}/pipelines/{p1['id']}").json()
    p2_fresh = api_client.get(f"/clients/{client['id']}/pipelines/{p2['id']}").json()

    assert p1_fresh["status"] == "paused"
    assert p2_fresh["status"] == "active"
    assert p1_fresh["lane"] != p2_fresh["lane"]
