"""Phase 06 API integration tests for extraction routes."""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.models.client import Client
from core.models.crawl import CrawlArtifact
from core.models.pipeline import Pipeline
from core.models.seed_lead import LeadImportBatch, SeedLeadRow


@pytest.fixture()
def pipeline(db: Session) -> Pipeline:
    client = Client(name="Acme", slug="acme-api06", status="active")
    db.add(client)
    db.flush()
    p = Pipeline(
        client_id=client.id,
        name="P06 API",
        slug="p06-api",
        lane="discovery",
        status="active",
    )
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def artifact(db: Session, pipeline: Pipeline) -> CrawlArtifact:
    a = CrawlArtifact(
        client_id=pipeline.client_id,
        pipeline_id=pipeline.id,
        artifact_type="html_page",
        url="https://saas-company.com/about",
        storage_key=f"artifacts/{pipeline.id}/html_page/{uuid.uuid4()}",
        status="stored",
        raw_metadata_json="saas cloud software platform hiring engineers",
    )
    db.add(a)
    db.flush()
    return a


@pytest.fixture()
def seed_row(db: Session, pipeline: Pipeline) -> SeedLeadRow:
    batch = LeadImportBatch(
        client_id=pipeline.client_id,
        pipeline_id=pipeline.id,
        filename="l.csv",
        original_name="l.csv",
        mime_type="text/csv",
        size_bytes=10,
        storage_key=f"lead_imports/{pipeline.id}/l.csv",
        status="completed",
        total_rows=1,
        valid_rows=1,
        error_rows=0,
    )
    db.add(batch)
    db.flush()
    row = SeedLeadRow(
        batch_id=batch.id,
        client_id=pipeline.client_id,
        pipeline_id=pipeline.id,
        row_index=0,
        original_first_name="eve",
        original_company="saas company",
        original_source="LinkedIn",
        raw_values="{}",
        normalized_first_name="Eve",
        normalized_company="Saas Company",
        normalized_source="LinkedIn",
        status="valid",
        is_duplicate=False,
    )
    db.add(row)
    db.flush()
    return row


def prefix(pipeline: Pipeline) -> str:
    return f"/clients/{pipeline.client_id}/pipelines/{pipeline.id}"


# ── Full extraction workflow ──────────────────────────────────────────────────

class TestRunExtractionAPI:
    def test_run_extraction_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/run",
            json={"crawl_artifact_id": str(artifact.id), "use_llm_fallback": False},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "classification" in data
        assert "companies" in data
        assert "signals" in data
        assert "contacts" in data

    def test_run_extraction_404_for_missing_artifact(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/run",
            json={"crawl_artifact_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404


# ── Classification ────────────────────────────────────────────────────────────

class TestClassifyAPI:
    def test_classify_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/classify",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "page_type" in data
        assert "relevance_score" in data

    def test_classify_404_for_missing_artifact(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/classify",
            json={"crawl_artifact_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404


# ── Companies ─────────────────────────────────────────────────────────────────

class TestCompaniesAPI:
    def test_list_companies_200(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.get(f"{prefix(pipeline)}/extraction/companies")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_extract_companies_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        assert resp.status_code == 201
        assert len(resp.json()) >= 1

    def test_get_company_200(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        create_resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        company_id = create_resp.json()[0]["id"]
        resp = api_client.get(f"{prefix(pipeline)}/extraction/companies/{company_id}")
        assert resp.status_code == 200

    def test_get_company_404(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.get(f"{prefix(pipeline)}/extraction/companies/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_list_companies_filter_review_status(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        resp = api_client.get(f"{prefix(pipeline)}/extraction/companies?review_status=pending")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ── Signals ───────────────────────────────────────────────────────────────────

class TestSignalsAPI:
    def test_list_signals_200(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.get(f"{prefix(pipeline)}/extraction/signals")
        assert resp.status_code == 200

    def test_extract_signals_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-signals",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        assert resp.status_code == 201
        assert isinstance(resp.json(), list)


# ── Contacts ──────────────────────────────────────────────────────────────────

class TestContactsAPI:
    def test_list_contacts_200(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.get(f"{prefix(pipeline)}/extraction/contacts")
        assert resp.status_code == 200

    def test_extract_contacts_with_llm_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-contacts",
            json={"crawl_artifact_id": str(artifact.id), "use_llm_fallback": True},
        )
        assert resp.status_code == 201
        data = resp.json()
        for contact in data:
            assert "email" not in contact or contact.get("email") is None


# ── Profile candidates ────────────────────────────────────────────────────────

class TestProfileCandidatesAPI:
    def test_list_candidates_200(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.get(f"{prefix(pipeline)}/extraction/profile-candidates")
        assert resp.status_code == 200

    def test_rank_profiles_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact, seed_row: SeedLeadRow):
        api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/rank-profiles",
            json={"seed_lead_row_id": str(seed_row.id)},
        )
        assert resp.status_code == 201
        candidates = resp.json()
        assert len(candidates) >= 1
        assert "rank" in candidates[0]
        assert "confidence" in candidates[0]

    def test_rank_profiles_404_for_missing_row(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/extraction/rank-profiles",
            json={"seed_lead_row_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404


# ── Enrichment ────────────────────────────────────────────────────────────────

class TestEnrichmentAPI:
    def test_enrich_contact_201(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/enrichment",
            json={"first_name": "Alice", "domain": "acme.com", "company": "Acme"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "completed"
        assert "email" in data
        assert "***" in (data["email"] or "")

    def test_enrichment_never_exposes_raw_secrets(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/enrichment",
            json={"first_name": "Bob"},
        )
        data = resp.json()
        assert data.get("provenance") is not None
        assert "secret" not in str(data).lower()

    def test_list_enrichment_200(self, api_client: TestClient, pipeline: Pipeline):
        api_client.post(f"{prefix(pipeline)}/enrichment", json={"first_name": "Carol"})
        resp = api_client.get(f"{prefix(pipeline)}/enrichment")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_enrichment_filter_by_status(self, api_client: TestClient, pipeline: Pipeline):
        api_client.post(f"{prefix(pipeline)}/enrichment", json={"first_name": "Dan"})
        resp = api_client.get(f"{prefix(pipeline)}/enrichment?status=completed")
        assert resp.status_code == 200
        assert all(r["status"] == "completed" for r in resp.json())


# ── Email verification ────────────────────────────────────────────────────────

class TestEmailVerificationAPI:
    def test_verify_email_201_verified(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/email-verification",
            json={"email": "alice@example.com"},
        )
        assert resp.status_code == 201
        assert resp.json()["verification_status"] == "verified"
        assert resp.json()["is_risky"] is False

    def test_verify_email_risky(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/email-verification",
            json={"email": "user@risky.com"},
        )
        assert resp.json()["verification_status"] == "risky"
        assert resp.json()["is_risky"] is True

    def test_verify_email_invalid(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/email-verification",
            json={"email": "user@invalid.com"},
        )
        assert resp.json()["verification_status"] == "invalid"

    def test_verify_email_unknown(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/email-verification",
            json={"email": "user@unknown.com"},
        )
        assert resp.json()["verification_status"] == "unknown"

    def test_list_verification_200(self, api_client: TestClient, pipeline: Pipeline):
        api_client.post(f"{prefix(pipeline)}/email-verification", json={"email": "a@b.com"})
        resp = api_client.get(f"{prefix(pipeline)}/email-verification")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ── Research summaries ────────────────────────────────────────────────────────

class TestResearchSummariesAPI:
    def test_generate_summary_201(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        company_resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        company_id = company_resp.json()[0]["id"]
        resp = api_client.post(
            f"{prefix(pipeline)}/research-summaries",
            json={"extracted_company_id": company_id, "evidence_urls": ["https://saas-company.com"]},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["summary_text"]
        assert data["generator"] in ("mock_llm", "llm")

    def test_generate_summary_404_for_missing_company(self, api_client: TestClient, pipeline: Pipeline):
        resp = api_client.post(
            f"{prefix(pipeline)}/research-summaries",
            json={"extracted_company_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404

    def test_list_summaries_200(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        company_resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        company_id = company_resp.json()[0]["id"]
        api_client.post(
            f"{prefix(pipeline)}/research-summaries",
            json={"extracted_company_id": company_id},
        )
        resp = api_client.get(f"{prefix(pipeline)}/research-summaries")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_pipeline_isolation(self, api_client: TestClient, pipeline: Pipeline, artifact: CrawlArtifact):
        company_resp = api_client.post(
            f"{prefix(pipeline)}/extraction/extract-companies",
            json={"crawl_artifact_id": str(artifact.id)},
        )
        company_id = company_resp.json()[0]["id"]
        api_client.post(
            f"{prefix(pipeline)}/research-summaries",
            json={"extracted_company_id": company_id},
        )
        other_pipeline_id = uuid.uuid4()
        resp = api_client.get(f"/clients/{pipeline.client_id}/pipelines/{other_pipeline_id}/research-summaries")
        assert resp.status_code == 200
        assert resp.json() == []
