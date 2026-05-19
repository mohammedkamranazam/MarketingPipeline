"""Tests for Phase 06 extraction service."""
from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from core.adapters.base import AdapterInput
from core.adapters.mock_email_verifier import MockEmailVerifierAdapter
from core.adapters.mock_enrichment import MockEnrichmentAdapter
from core.adapters.mock_llm import MockLLMAdapter
from core.adapters.registry import ADAPTER_REGISTRY
from core.contracts.extraction import (
    EnrichContactRequest,
    GenerateSummaryRequest,
    VerifyEmailRequest,
)
from core.models.crawl import CrawlArtifact
from core.models.pipeline import Pipeline
from core.models.seed_lead import LeadImportBatch, SeedLeadRow
from core.services import extraction_service as svc


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def pipeline(db: Session) -> Pipeline:
    from core.models.client import Client
    client = Client(name="Acme", slug="acme", status="active")
    db.add(client)
    db.flush()
    p = Pipeline(
        client_id=client.id,
        name="P06 Pipeline",
        slug="p06-pipeline",
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
        url="https://example-saas.com/about",
        storage_key=f"artifacts/{pipeline.id}/html_page/{uuid.uuid4()}",
        status="stored",
        raw_metadata_json="We are a saas software platform. We are hiring engineers.",
    )
    db.add(a)
    db.flush()
    return a


@pytest.fixture()
def seed_row(db: Session, pipeline: Pipeline) -> SeedLeadRow:
    batch = LeadImportBatch(
        client_id=pipeline.client_id,
        pipeline_id=pipeline.id,
        filename="leads.csv",
        original_name="leads.csv",
        mime_type="text/csv",
        size_bytes=100,
        storage_key=f"lead_imports/{pipeline.id}/leads.csv",
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
        original_first_name="alice",
        original_company="example saas",
        original_source="LinkedIn",
        raw_values='{"first_name":"alice","company":"example saas"}',
        normalized_first_name="Alice",
        normalized_company="Example Saas",
        normalized_source="LinkedIn",
        status="valid",
        is_duplicate=False,
    )
    db.add(row)
    db.flush()
    return row


# ── Adapter certification ─────────────────────────────────────────────────────

class TestMockLLMAdapter:
    def test_in_registry(self):
        assert "mock_llm" in ADAPTER_REGISTRY

    def test_is_certified(self):
        assert MockLLMAdapter.META.is_certified

    def test_classify_returns_page_type(self):
        adapter = MockLLMAdapter()
        out = adapter.execute(AdapterInput("classify", {
            "content": "saas platform", "url": "https://ex.com"
        }))
        assert out.success
        data = out.data_dict()
        assert "page_type" in data
        assert "relevance_score" in data

    def test_extract_company_returns_name(self):
        adapter = MockLLMAdapter()
        out = adapter.execute(AdapterInput("extract_company", {
            "content": "software", "url": "https://acme.com"
        }))
        assert out.success
        assert "name" in out.data_dict()

    def test_extract_signals_returns_list(self):
        adapter = MockLLMAdapter()
        out = adapter.execute(AdapterInput(
            "extract_signals", {"content": "we are hiring engineers"}
        ))
        assert out.success
        assert "signals" in out.data_dict()

    def test_extract_contacts_returns_list(self):
        adapter = MockLLMAdapter()
        out = adapter.execute(AdapterInput(
            "extract_contacts", {"content": "team page", "url": "https://acme.com/team"}
        ))
        assert out.success
        assert "contacts" in out.data_dict()

    def test_summarize_returns_text(self):
        adapter = MockLLMAdapter()
        out = adapter.execute(AdapterInput("summarize", {
            "company_name": "Acme", "evidence_urls": ["https://acme.com"]
        }))
        assert out.success
        data = out.data_dict()
        assert "summary_text" in data
        assert "citations" in data

    def test_unknown_op_fails(self):
        adapter = MockLLMAdapter()
        out = adapter.execute(AdapterInput("bad_op", {}))
        assert not out.success

    def test_relevance_score_higher_for_saas_content(self):
        adapter = MockLLMAdapter()
        out_relevant = adapter.execute(AdapterInput("classify", {
            "content": "saas cloud platform", "url": "https://ex.com"
        }))
        out_plain = adapter.execute(AdapterInput("classify", {
            "content": "local bakery", "url": "https://bakery.com"
        }))
        saas_score = out_relevant.data_dict()["relevance_score"]
        plain_score = out_plain.data_dict()["relevance_score"]
        assert saas_score > plain_score


class TestMockEnrichmentAdapter:
    def test_in_registry(self):
        assert "mock_enrichment" in ADAPTER_REGISTRY

    def test_is_certified(self):
        assert MockEnrichmentAdapter.META.is_certified

    def test_enrich_contact_returns_masked_email(self):
        adapter = MockEnrichmentAdapter()
        out = adapter.execute(AdapterInput("enrich_contact", {
            "first_name": "Alice", "domain": "example.com", "company": "Acme"
        }))
        assert out.success
        data = out.data_dict()
        assert "email" in data
        assert "***" in data["email"]

    def test_enrich_contact_has_provenance(self):
        adapter = MockEnrichmentAdapter()
        out = adapter.execute(AdapterInput(
            "enrich_contact", {"first_name": "Bob", "domain": "test.com"}
        ))
        assert out.data_dict()["provenance"].startswith("mock_enrichment:")

    def test_unknown_op_fails(self):
        adapter = MockEnrichmentAdapter()
        out = adapter.execute(AdapterInput("bad_op", {}))
        assert not out.success


class TestMockEmailVerifierAdapter:
    def test_in_registry(self):
        assert "mock_email_verifier" in ADAPTER_REGISTRY

    def test_is_certified(self):
        assert MockEmailVerifierAdapter.META.is_certified

    def test_verified_for_normal_email(self):
        adapter = MockEmailVerifierAdapter()
        out = adapter.execute(AdapterInput("verify_email", {"email": "alice@example.com"}))
        assert out.success
        assert out.data_dict()["verification_status"] == "verified"
        assert out.data_dict()["is_risky"] is False

    def test_risky_for_risky_domain(self):
        adapter = MockEmailVerifierAdapter()
        out = adapter.execute(AdapterInput("verify_email", {"email": "user@risky.com"}))
        assert out.data_dict()["verification_status"] == "risky"
        assert out.data_dict()["is_risky"] is True

    def test_invalid_for_invalid_domain(self):
        adapter = MockEmailVerifierAdapter()
        out = adapter.execute(AdapterInput("verify_email", {"email": "user@invalid.com"}))
        assert out.data_dict()["verification_status"] == "invalid"

    def test_unknown_for_unknown_domain(self):
        adapter = MockEmailVerifierAdapter()
        out = adapter.execute(AdapterInput("verify_email", {"email": "user@unknown.com"}))
        assert out.data_dict()["verification_status"] == "unknown"

    def test_has_provenance_and_request_id(self):
        adapter = MockEmailVerifierAdapter()
        out = adapter.execute(AdapterInput("verify_email", {"email": "a@b.com"}))
        data = out.data_dict()
        assert "provenance" in data
        assert "provider_request_id" in data

    def test_unknown_op_fails(self):
        adapter = MockEmailVerifierAdapter()
        out = adapter.execute(AdapterInput("bad_op", {}))
        assert not out.success


# ── Classify artifact ─────────────────────────────────────────────────────────

class TestClassifyArtifact:
    def test_rule_classifier_sets_page_type(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        result = svc.classify_artifact(db, pipeline.client_id, pipeline.id, artifact.id)
        assert result.page_type in [
            "company_homepage", "team_page", "about_page", "blog_post", "pricing_page"
        ]
        assert result.classifier in ("rule", "mock_llm")

    def test_llm_fallback_sets_classifier(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        result = svc.classify_artifact(
            db, pipeline.client_id, pipeline.id, artifact.id, use_llm_fallback=True
        )
        assert result.classifier in ("rule", "mock_llm")

    def test_raises_for_wrong_pipeline(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        with pytest.raises(ValueError, match="not found"):
            svc.classify_artifact(db, pipeline.client_id, uuid.uuid4(), artifact.id)

    def test_raises_for_missing_artifact(self, db: Session, pipeline: Pipeline):
        with pytest.raises(ValueError, match="not found"):
            svc.classify_artifact(db, pipeline.client_id, pipeline.id, uuid.uuid4())

    def test_saas_content_has_higher_relevance(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        result = svc.classify_artifact(db, pipeline.client_id, pipeline.id, artifact.id)
        assert result.relevance_score >= 0.3


# ── Extract companies ─────────────────────────────────────────────────────────

class TestExtractCompanies:
    def test_rule_extractor_creates_company(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        assert len(companies) == 1
        assert companies[0].name
        assert companies[0].extractor in ("rule", "mock_llm")
        assert companies[0].pipeline_id == pipeline.id

    def test_llm_fallback_creates_company(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(
            db, pipeline.client_id, pipeline.id, artifact.id, use_llm_fallback=True
        )
        assert len(companies) == 1

    def test_raises_for_wrong_pipeline(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        with pytest.raises(ValueError):
            svc.extract_companies(db, pipeline.client_id, uuid.uuid4(), artifact.id)

    def test_company_has_evidence(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        assert companies[0].evidence_url or companies[0].evidence_text

    def test_pipeline_isolation(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        other_id = uuid.uuid4()
        results = svc.list_companies(db, pipeline.client_id, other_id)
        assert results == []


# ── Extract signals ───────────────────────────────────────────────────────────

class TestExtractSignals:
    def test_hiring_signal_detected(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        signals = svc.extract_signals(db, pipeline.client_id, pipeline.id, artifact.id)
        types = [s.signal_type for s in signals]
        assert "hiring" in types

    def test_llm_fallback_returns_signals(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        signals = svc.extract_signals(
            db, pipeline.client_id, pipeline.id, artifact.id, use_llm_fallback=True
        )
        assert len(signals) >= 1

    def test_raises_for_wrong_pipeline(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        with pytest.raises(ValueError):
            svc.extract_signals(db, pipeline.client_id, uuid.uuid4(), artifact.id)

    def test_pipeline_isolation(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        svc.extract_signals(db, pipeline.client_id, pipeline.id, artifact.id)
        results = svc.list_signals(db, pipeline.client_id, uuid.uuid4())
        assert results == []


# ── Extract contacts ──────────────────────────────────────────────────────────

class TestExtractContacts:
    def test_rule_returns_empty_list(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        contacts = svc.extract_contacts(db, pipeline.client_id, pipeline.id, artifact.id)
        assert contacts == []

    def test_llm_fallback_returns_contacts(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        contacts = svc.extract_contacts(
            db, pipeline.client_id, pipeline.id, artifact.id, use_llm_fallback=True
        )
        assert len(contacts) >= 1

    def test_contacts_have_no_email(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        contacts = svc.extract_contacts(
            db, pipeline.client_id, pipeline.id, artifact.id, use_llm_fallback=True
        )
        for c in contacts:
            assert not hasattr(c, "email") or getattr(c, "email", None) is None

    def test_raises_for_wrong_pipeline(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        with pytest.raises(ValueError):
            svc.extract_contacts(db, pipeline.client_id, uuid.uuid4(), artifact.id)


# ── Full extraction workflow ──────────────────────────────────────────────────

class TestRunExtraction:
    def test_returns_all_components(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        result = svc.run_extraction(db, pipeline.client_id, pipeline.id, artifact.id)
        assert result.classification.page_type
        assert len(result.companies) >= 1
        assert isinstance(result.signals, list)
        assert isinstance(result.contacts, list)

    def test_raises_for_missing_artifact(self, db: Session, pipeline: Pipeline):
        with pytest.raises(ValueError):
            svc.run_extraction(db, pipeline.client_id, pipeline.id, uuid.uuid4())


# ── Retrieval ─────────────────────────────────────────────────────────────────

class TestRetrieval:
    def test_list_companies_filter_by_review_status(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        pending = svc.list_companies(
            db, pipeline.client_id, pipeline.id, review_status="pending"
        )
        assert len(pending) >= 1

    def test_get_company_returns_none_cross_pipeline(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        result = svc.get_company(db, pipeline.client_id, uuid.uuid4(), companies[0].id)
        assert result is None

    def test_list_signals_filter_by_company(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        svc.extract_signals(db, pipeline.client_id, pipeline.id, artifact.id, companies[0].id)
        results = svc.list_signals(db, pipeline.client_id, pipeline.id, companies[0].id)
        assert all(s.extracted_company_id == companies[0].id for s in results)

    def test_list_contacts_filter_by_company(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        svc.extract_contacts(
            db, pipeline.client_id, pipeline.id, artifact.id,
            companies[0].id, use_llm_fallback=True,
        )
        results = svc.list_contacts(db, pipeline.client_id, pipeline.id, companies[0].id)
        assert all(c.extracted_company_id == companies[0].id for c in results)


# ── Seed lead resolver ────────────────────────────────────────────────────────

class TestSeedLeadResolver:
    def test_creates_company_from_seed_row(
        self, db: Session, pipeline: Pipeline, seed_row: SeedLeadRow
    ):
        companies = svc.resolve_seed_lead_companies(
            db, pipeline.client_id, pipeline.id, seed_row.id
        )
        assert len(companies) == 1
        assert companies[0].seed_lead_row_id == seed_row.id
        assert companies[0].name

    def test_raises_for_wrong_pipeline(
        self, db: Session, pipeline: Pipeline, seed_row: SeedLeadRow
    ):
        with pytest.raises(ValueError):
            svc.resolve_seed_lead_companies(
                db, pipeline.client_id, uuid.uuid4(), seed_row.id
            )

    def test_raises_for_missing_row(self, db: Session, pipeline: Pipeline):
        with pytest.raises(ValueError):
            svc.resolve_seed_lead_companies(
                db, pipeline.client_id, pipeline.id, uuid.uuid4()
            )


# ── Profile candidate ranking ─────────────────────────────────────────────────

class TestProfileCandidates:
    def test_rank_creates_candidates(
        self,
        db: Session,
        pipeline: Pipeline,
        artifact: CrawlArtifact,
        seed_row: SeedLeadRow,
    ):
        svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        candidates = svc.rank_profile_candidates(
            db, pipeline.client_id, pipeline.id, seed_row.id
        )
        assert len(candidates) >= 1
        assert candidates[0].seed_lead_row_id == seed_row.id

    def test_candidates_ordered_by_rank(
        self,
        db: Session,
        pipeline: Pipeline,
        artifact: CrawlArtifact,
        seed_row: SeedLeadRow,
    ):
        svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        svc.rank_profile_candidates(db, pipeline.client_id, pipeline.id, seed_row.id)
        listed = svc.list_profile_candidates(db, pipeline.client_id, pipeline.id, seed_row.id)
        ranks = [c.rank for c in listed]
        assert ranks == sorted(ranks)

    def test_pipeline_isolation(self, db: Session, pipeline: Pipeline, seed_row: SeedLeadRow):
        results = svc.list_profile_candidates(db, pipeline.client_id, uuid.uuid4())
        assert results == []

    def test_raises_for_missing_seed_row(self, db: Session, pipeline: Pipeline):
        with pytest.raises(ValueError):
            svc.rank_profile_candidates(db, pipeline.client_id, pipeline.id, uuid.uuid4())


# ── Enrichment ────────────────────────────────────────────────────────────────

class TestEnrichment:
    def test_enrich_contact_creates_record(self, db: Session, pipeline: Pipeline):
        request = EnrichContactRequest(first_name="Alice", domain="acme.com", company="Acme")
        record = svc.enrich_contact(db, pipeline.client_id, pipeline.id, request)
        assert record.status == "completed"
        assert record.email
        assert "***" in (record.email or "")
        assert record.provenance

    def test_enrichment_has_provider_request_id(self, db: Session, pipeline: Pipeline):
        request = EnrichContactRequest(first_name="Bob")
        record = svc.enrich_contact(db, pipeline.client_id, pipeline.id, request)
        assert record.provider_request_id

    def test_list_enrichment_filter_by_status(self, db: Session, pipeline: Pipeline):
        request = EnrichContactRequest(first_name="Carol")
        svc.enrich_contact(db, pipeline.client_id, pipeline.id, request)
        completed = svc.list_enrichment_records(
            db, pipeline.client_id, pipeline.id, "completed"
        )
        assert len(completed) >= 1

    def test_pipeline_isolation(self, db: Session, pipeline: Pipeline):
        request = EnrichContactRequest(first_name="Dan")
        svc.enrich_contact(db, pipeline.client_id, pipeline.id, request)
        other = svc.list_enrichment_records(db, pipeline.client_id, uuid.uuid4())
        assert other == []


# ── Email verification ────────────────────────────────────────────────────────

class TestEmailVerification:
    def test_verified_email(self, db: Session, pipeline: Pipeline):
        request = VerifyEmailRequest(email="alice@example.com")
        record = svc.verify_email(db, pipeline.client_id, pipeline.id, request)
        assert record.verification_status == "verified"
        assert record.is_risky is False

    def test_risky_email(self, db: Session, pipeline: Pipeline):
        request = VerifyEmailRequest(email="user@risky.com")
        record = svc.verify_email(db, pipeline.client_id, pipeline.id, request)
        assert record.verification_status == "risky"
        assert record.is_risky is True

    def test_invalid_email(self, db: Session, pipeline: Pipeline):
        request = VerifyEmailRequest(email="user@invalid.com")
        record = svc.verify_email(db, pipeline.client_id, pipeline.id, request)
        assert record.verification_status == "invalid"

    def test_unknown_email(self, db: Session, pipeline: Pipeline):
        request = VerifyEmailRequest(email="user@unknown.com")
        record = svc.verify_email(db, pipeline.client_id, pipeline.id, request)
        assert record.verification_status == "unknown"

    def test_pipeline_isolation(self, db: Session, pipeline: Pipeline):
        request = VerifyEmailRequest(email="x@example.com")
        svc.verify_email(db, pipeline.client_id, pipeline.id, request)
        other = svc.list_verification_records(db, pipeline.client_id, uuid.uuid4())
        assert other == []

    def test_list_filter_by_status(self, db: Session, pipeline: Pipeline):
        svc.verify_email(
            db, pipeline.client_id, pipeline.id, VerifyEmailRequest(email="a@example.com")
        )
        verified = svc.list_verification_records(
            db, pipeline.client_id, pipeline.id, "verified"
        )
        assert len(verified) >= 1


# ── Research summaries ────────────────────────────────────────────────────────

class TestResearchSummaries:
    def test_generate_summary_creates_record(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        req = GenerateSummaryRequest(
            extracted_company_id=companies[0].id,
            evidence_urls=["https://example-saas.com/about"],
        )
        summary = svc.generate_summary(db, pipeline.client_id, pipeline.id, req)
        assert summary.summary_text
        assert summary.generator in ("mock_llm", "llm")

    def test_summary_includes_citations(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        req = GenerateSummaryRequest(
            extracted_company_id=companies[0].id,
            evidence_urls=["https://example.com"],
        )
        summary = svc.generate_summary(db, pipeline.client_id, pipeline.id, req)
        assert summary.citations_json is not None

    def test_raises_for_missing_company(self, db: Session, pipeline: Pipeline):
        req = GenerateSummaryRequest(extracted_company_id=uuid.uuid4())
        with pytest.raises(ValueError):
            svc.generate_summary(db, pipeline.client_id, pipeline.id, req)

    def test_pipeline_isolation(
        self, db: Session, pipeline: Pipeline, artifact: CrawlArtifact
    ):
        companies = svc.extract_companies(db, pipeline.client_id, pipeline.id, artifact.id)
        req = GenerateSummaryRequest(extracted_company_id=companies[0].id)
        svc.generate_summary(db, pipeline.client_id, pipeline.id, req)
        other = svc.list_summaries(db, pipeline.client_id, uuid.uuid4())
        assert other == []
