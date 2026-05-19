"""
Tests for source_service.

Acceptance criteria tested:
- create_source_connector persists connector scoped to client/pipeline.
- list_source_connectors filters by source_type.
- get_source_connector returns None for cross-pipeline access.
- update_source_connector applies partial update; raises ValueError when not found.
- delete_source_connector returns True; False for cross-pipeline.
- create_policy_rule persists rule.
- list_policy_rules returns rules ordered by priority asc.
- delete_policy_rule returns False for cross-pipeline.
- decide_policy returns allow when URL matches allow rule.
- decide_policy returns block when URL matches block rule.
- decide_policy returns review (default) when no rule matches.
- decide_policy matches by source entity_id.
- submit_url_candidate stores URL; idempotent on duplicate.
- submit_url_candidate applies policy to set policy_decision.
- list_url_candidates filters by status.
- test_source_connector returns success for certified adapter.
- test_source_connector returns error for uncertified adapter.
- test_source_connector returns error for unknown connector.
- register_adapter creates new entry; updates existing.
- list_adapters returns all adapters.
- create_credential_profile persists profile with status=active.
- get_credential_profile returns None for cross-pipeline.
- update_credential_profile applies partial update.
- validate_credential sets status=expired on expired credential.
- validate_credential passes for non-expired credential.
- check_preflight raises ValueError when credential is not active.
- Pipeline isolation across all entities.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from core.contracts.source import (
    AdapterRegistryCreate,
    CredentialProfileCreate,
    CredentialProfileUpdate,
    PolicyDecisionRequest,
    PolicyRuleCreate,
    SourceConnectorCreate,
    SourceConnectorUpdate,
    URLCandidateCreate,
)
from core.models.client import Client
from core.models.pipeline import Pipeline
from core.services import source_service


def _create_client(db) -> Client:
    c = Client(name=f"C-{uuid.uuid4()}", slug=f"c-{uuid.uuid4()}", status="active")
    db.add(c)
    db.flush()
    return c


def _create_pipeline(db, client_id: uuid.UUID) -> Pipeline:
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


def _connector_payload(**kw) -> SourceConnectorCreate:
    defaults = dict(source_type="public_web", name="My Source", adapter_key="mock_search")
    defaults.update(kw)
    return SourceConnectorCreate(**defaults)


def _rule_payload(**kw) -> PolicyRuleCreate:
    defaults = dict(entity_type="url_pattern", pattern="https://allowed.com", decision="allow")
    defaults.update(kw)
    return PolicyRuleCreate(**defaults)


def _credential_payload(**kw) -> CredentialProfileCreate:
    defaults = dict(
        name="My Cred",
        adapter_key="mock_search",
        secret_reference="env:MY_API_KEY",
        scopes=["read"],
    )
    defaults.update(kw)
    return CredentialProfileCreate(**defaults)


def _adapter_payload(**kw) -> AdapterRegistryCreate:
    defaults = dict(
        adapter_key="mock_search",
        display_name="Mock Search",
        source_type="search_provider",
        audit_event_type="search.mock.executed",
        is_certified=True,
    )
    defaults.update(kw)
    return AdapterRegistryCreate(**defaults)


# ── SourceConnector ───────────────────────────────────────────────────────────

def test_create_source_connector(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    conn = source_service.create_source_connector(db, c.id, p.id, _connector_payload())
    assert conn.pipeline_id == p.id
    assert conn.status == "active"


def test_list_source_connectors_type_filter(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_source_connector(
        db, c.id, p.id, _connector_payload(source_type="public_web")
    )
    source_service.create_source_connector(
        db, c.id, p.id, _connector_payload(source_type="search_provider", name="S2")
    )
    web = source_service.list_source_connectors(db, c.id, p.id, source_type="public_web")
    search = source_service.list_source_connectors(db, c.id, p.id, source_type="search_provider")
    assert len(web) == 1
    assert len(search) == 1


def test_get_source_connector_cross_pipeline_none(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    conn = source_service.create_source_connector(db, c.id, p_a.id, _connector_payload())
    assert source_service.get_source_connector(db, c.id, p_b.id, conn.id) is None


def test_update_source_connector(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    conn = source_service.create_source_connector(db, c.id, p.id, _connector_payload())
    updated = source_service.update_source_connector(
        db, c.id, p.id, conn.id, SourceConnectorUpdate(name="Updated Name", status="paused")
    )
    assert updated.name == "Updated Name"
    assert updated.status == "paused"


def test_update_source_connector_not_found_raises(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    with pytest.raises(ValueError, match="not found"):
        source_service.update_source_connector(
            db, c.id, p.id, uuid.uuid4(), SourceConnectorUpdate(name="x")
        )


def test_delete_source_connector(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    conn = source_service.create_source_connector(db, c.id, p.id, _connector_payload())
    assert source_service.delete_source_connector(db, c.id, p.id, conn.id) is True
    assert source_service.list_source_connectors(db, c.id, p.id) == []


def test_delete_source_connector_cross_pipeline_false(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    conn = source_service.create_source_connector(db, c.id, p_a.id, _connector_payload())
    assert source_service.delete_source_connector(db, c.id, p_b.id, conn.id) is False


# ── PolicyRule ────────────────────────────────────────────────────────────────

def test_create_policy_rule(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    rule = source_service.create_policy_rule(db, c.id, p.id, _rule_payload())
    assert rule.decision == "allow"
    assert rule.pipeline_id == p.id


def test_list_policy_rules_ordered_priority(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(priority=200))
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(priority=50))
    rules = source_service.list_policy_rules(db, c.id, p.id)
    assert rules[0].priority == 50
    assert rules[1].priority == 200


def test_delete_policy_rule_cross_pipeline_false(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    rule = source_service.create_policy_rule(db, c.id, p_a.id, _rule_payload())
    assert source_service.delete_policy_rule(db, c.id, p_b.id, rule.id) is False


# ── Policy decisions ──────────────────────────────────────────────────────────

def test_decide_policy_allow_url(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="url_pattern", pattern="https://allowed.com", decision="allow"
    ))
    result = source_service.decide_policy(db, c.id, p.id, PolicyDecisionRequest(
        operation_type="fetch", url="https://allowed.com/page"
    ))
    assert result.decision == "allow"
    assert result.matched_rule_id is not None


def test_decide_policy_block_url(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="url_pattern", pattern="https://blocked.com", decision="block"
    ))
    result = source_service.decide_policy(db, c.id, p.id, PolicyDecisionRequest(
        operation_type="fetch", url="https://blocked.com/anything"
    ))
    assert result.decision == "block"


def test_decide_policy_default_review(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    result = source_service.decide_policy(db, c.id, p.id, PolicyDecisionRequest(
        operation_type="fetch", url="https://unknown.com"
    ))
    assert result.decision == "review"
    assert result.matched_rule_id is None


def test_decide_policy_priority_first_wins(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="url_pattern", pattern="https://x.com", decision="block", priority=200
    ))
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="url_pattern", pattern="https://x.com", decision="allow", priority=10
    ))
    result = source_service.decide_policy(db, c.id, p.id, PolicyDecisionRequest(
        operation_type="fetch", url="https://x.com/page"
    ))
    assert result.decision == "allow"


def test_decide_policy_source_entity(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    conn = source_service.create_source_connector(db, c.id, p.id, _connector_payload())
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="source", entity_id=conn.id, pattern=None, decision="block"
    ))
    result = source_service.decide_policy(db, c.id, p.id, PolicyDecisionRequest(
        operation_type="fetch", source_connector_id=conn.id
    ))
    assert result.decision == "block"


# ── URLCandidate ──────────────────────────────────────────────────────────────

def test_submit_url_candidate_idempotent(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    u1 = source_service.submit_url_candidate(db, c.id, p.id, URLCandidateCreate(url="https://ex.com"))
    u2 = source_service.submit_url_candidate(db, c.id, p.id, URLCandidateCreate(url="https://ex.com"))
    assert u1.id == u2.id
    assert len(source_service.list_url_candidates(db, c.id, p.id)) == 1


def test_submit_url_candidate_applies_policy(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="url_pattern", pattern="https://allowed.com", decision="allow"
    ))
    u = source_service.submit_url_candidate(
        db, c.id, p.id, URLCandidateCreate(url="https://allowed.com/page")
    )
    assert u.policy_decision == "allow"


def test_list_url_candidates_status_filter(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p.id, _rule_payload(
        entity_type="url_pattern", pattern="https://ok.com", decision="allow"
    ))
    source_service.submit_url_candidate(db, c.id, p.id, URLCandidateCreate(url="https://ok.com/1"))
    source_service.submit_url_candidate(db, c.id, p.id, URLCandidateCreate(url="https://unknown.com"))
    allowed = source_service.list_url_candidates(db, c.id, p.id, status="allow")
    review = source_service.list_url_candidates(db, c.id, p.id, status="review")
    assert len(allowed) == 1
    assert len(review) == 1


# ── Adapter and connector test ────────────────────────────────────────────────

def test_test_source_connector_certified(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.register_adapter(db, _adapter_payload(is_certified=True))
    conn = source_service.create_source_connector(db, c.id, p.id, _connector_payload())
    result = source_service.test_source_connector(db, c.id, p.id, conn.id)
    assert result.success is True
    assert result.latency_ms is not None


def test_test_source_connector_uncertified(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    source_service.register_adapter(db, _adapter_payload(is_certified=False))
    conn = source_service.create_source_connector(db, c.id, p.id, _connector_payload())
    result = source_service.test_source_connector(db, c.id, p.id, conn.id)
    assert result.success is False
    assert result.error is not None


def test_test_source_connector_not_found(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    result = source_service.test_source_connector(db, c.id, p.id, uuid.uuid4())
    assert result.success is False


def test_register_adapter_upserts(db):
    source_service.register_adapter(db, _adapter_payload(display_name="First"))
    source_service.register_adapter(db, _adapter_payload(display_name="Updated"))
    adapters = source_service.list_adapters(db)
    mock = next(a for a in adapters if a.adapter_key == "mock_search")
    assert mock.display_name == "Updated"


# ── CredentialProfile ─────────────────────────────────────────────────────────

def test_create_credential_profile(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    profile = source_service.create_credential_profile(db, c.id, p.id, _credential_payload())
    assert profile.status == "active"
    assert profile.pipeline_id == p.id


def test_get_credential_cross_pipeline_none(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    profile = source_service.create_credential_profile(db, c.id, p_a.id, _credential_payload())
    assert source_service.get_credential_profile(db, c.id, p_b.id, profile.id) is None


def test_update_credential_profile(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    profile = source_service.create_credential_profile(db, c.id, p.id, _credential_payload())
    updated = source_service.update_credential_profile(
        db, c.id, p.id, profile.id,
        CredentialProfileUpdate(status="expiring", scopes=["read", "write"])
    )
    assert updated.status == "expiring"


def test_validate_credential_passes(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    profile = source_service.create_credential_profile(db, c.id, p.id, _credential_payload())
    run = source_service.validate_credential(db, c.id, p.id, profile.id)
    assert run.status == "passed"
    refreshed = source_service.get_credential_profile(db, c.id, p.id, profile.id)
    assert refreshed is not None
    assert refreshed.last_validated_at is not None


def test_validate_credential_expired(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    past = datetime.now(UTC) - timedelta(days=1)
    profile = source_service.create_credential_profile(
        db, c.id, p.id, _credential_payload(expires_at=past)
    )
    run = source_service.validate_credential(db, c.id, p.id, profile.id)
    assert run.status == "failed"
    assert "expired" in (run.reason or "")
    refreshed = source_service.get_credential_profile(db, c.id, p.id, profile.id)
    assert refreshed is not None and refreshed.status == "expired"


def test_check_preflight_active_passes(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    profile = source_service.create_credential_profile(db, c.id, p.id, _credential_payload())
    source_service.check_preflight(db, c.id, p.id, profile.id)  # must not raise


def test_check_preflight_non_active_raises(db):
    c = _create_client(db)
    p = _create_pipeline(db, c.id)
    profile = source_service.create_credential_profile(db, c.id, p.id, _credential_payload())
    source_service.update_credential_profile(
        db, c.id, p.id, profile.id, CredentialProfileUpdate(status="expired")
    )
    with pytest.raises(ValueError, match="not active"):
        source_service.check_preflight(db, c.id, p.id, profile.id)


# ── Pipeline isolation ────────────────────────────────────────────────────────

def test_connectors_pipeline_isolation(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    source_service.create_source_connector(db, c.id, p_a.id, _connector_payload())
    assert source_service.list_source_connectors(db, c.id, p_b.id) == []


def test_policy_rules_pipeline_isolation(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    source_service.create_policy_rule(db, c.id, p_a.id, _rule_payload())
    assert source_service.list_policy_rules(db, c.id, p_b.id) == []


def test_credentials_pipeline_isolation(db):
    c = _create_client(db)
    p_a = _create_pipeline(db, c.id)
    p_b = _create_pipeline(db, c.id)
    source_service.create_credential_profile(db, c.id, p_a.id, _credential_payload())
    assert source_service.list_credential_profiles(db, c.id, p_b.id) == []
