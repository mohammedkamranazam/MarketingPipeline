"""
Tests for the documents and lead-imports API routes.

Acceptance criteria tested:
- POST /clients/{cid}/pipelines/{pid}/documents returns 201 with DocumentUploadResponse.
- POST with unsupported mime_type returns 422.
- GET /documents returns list of documents for the pipeline.
- GET /documents/{id} returns 404 when not found.
- GET /documents/{id}/knowledge returns empty list initially.
- POST /lead-imports returns 201 with LeadImportBatchResponse.
- POST /lead-imports with unsupported mime_type returns 422.
- GET /lead-imports returns list for the pipeline.
- GET /lead-imports/{id}/rows returns empty list for unprocessed batch.
- Cross-pipeline isolation: uploading to pipeline A does not appear in pipeline B.
"""

import csv
import io
import uuid


def _make_csv_bytes(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode()


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


# ---------------------------------------------------------------------------
# Document upload
# ---------------------------------------------------------------------------

def test_upload_document_returns_201(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/documents"
    r = api_client.post(
        url,
        files={"file": ("test.txt", b"Hello content", "text/plain")},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["original_name"] == "test.txt"
    assert body["pipeline_id"] == pipeline["id"]


def test_upload_document_unsupported_mime_returns_422(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/documents"
    r = api_client.post(
        url,
        files={"file": ("file.zip", b"data", "application/zip")},
    )
    assert r.status_code == 422


def test_list_documents_returns_list(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/documents"
    api_client.post(url, files={"file": ("a.txt", b"Content A", "text/plain")})
    api_client.post(url, files={"file": ("b.txt", b"Content B", "text/plain")})
    r = api_client.get(url)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_document_not_found_returns_404(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/documents/{uuid.uuid4()}"
    r = api_client.get(url)
    assert r.status_code == 404


def test_get_knowledge_items_empty_initially(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    base_url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/documents"
    upload = api_client.post(base_url, files={"file": ("c.txt", b"Text", "text/plain")})
    doc_id = upload.json()["id"]
    r = api_client.get(f"{base_url}/{doc_id}/knowledge")
    assert r.status_code == 200
    assert r.json() == []


def test_document_isolation_across_pipelines(api_client):
    client = _create_client(api_client)
    p1 = _create_pipeline(api_client, client["id"])
    p2 = _create_pipeline(api_client, client["id"])
    url1 = f"/clients/{client['id']}/pipelines/{p1['id']}/documents"
    url2 = f"/clients/{client['id']}/pipelines/{p2['id']}/documents"
    api_client.post(url1, files={"file": ("d.txt", b"P1 only", "text/plain")})
    assert api_client.get(url2).json() == []


# ---------------------------------------------------------------------------
# Lead import upload
# ---------------------------------------------------------------------------

def test_upload_lead_import_returns_201(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/lead-imports"
    data = _make_csv_bytes([{"first_name": "Alice", "company": "Acme"}])
    r = api_client.post(
        url,
        files={"file": ("leads.csv", data, "text/csv")},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["original_name"] == "leads.csv"


def test_upload_lead_import_unsupported_mime_returns_422(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/lead-imports"
    r = api_client.post(
        url,
        files={"file": ("file.pdf", b"data", "application/pdf")},
    )
    assert r.status_code == 422


def test_list_lead_imports_returns_list(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/lead-imports"
    data = _make_csv_bytes([{"first_name": "Alice", "company": "Acme"}])
    api_client.post(url, files={"file": ("a.csv", data, "text/csv")})
    api_client.post(url, files={"file": ("b.csv", data, "text/csv")})
    r = api_client.get(url)
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_rows_empty_initially(api_client):
    client = _create_client(api_client)
    pipeline = _create_pipeline(api_client, client["id"])
    url = f"/clients/{client['id']}/pipelines/{pipeline['id']}/lead-imports"
    data = _make_csv_bytes([{"first_name": "Alice", "company": "Acme"}])
    batch_id = api_client.post(url, files={"file": ("c.csv", data, "text/csv")}).json()["id"]
    r = api_client.get(f"{url}/{batch_id}/rows")
    assert r.status_code == 200
    assert r.json() == []


def test_lead_import_isolation_across_pipelines(api_client):
    client = _create_client(api_client)
    p1 = _create_pipeline(api_client, client["id"])
    p2 = _create_pipeline(api_client, client["id"])
    url1 = f"/clients/{client['id']}/pipelines/{p1['id']}/lead-imports"
    url2 = f"/clients/{client['id']}/pipelines/{p2['id']}/lead-imports"
    data = _make_csv_bytes([{"first_name": "Alice", "company": "Acme"}])
    api_client.post(url1, files={"file": ("a.csv", data, "text/csv")})
    assert api_client.get(url2).json() == []
