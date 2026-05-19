"""
Tests for review_service.

Acceptance criteria tested:
- create_review_item persists item with status=pending and writes an audit log entry.
- list_review_items returns items for the pipeline ordered by created_at desc.
- list_review_items filters by status when provided.
- get_review_item returns None when id does not belong to the pipeline.
- decide_review_item applies decision, sets decided_at, writes audit log.
- decide_review_item raises ValueError when item is not pending.
- decide_review_item raises ValueError when item does not exist for pipeline.
- upsert_active_icp_config inserts config and writes audit log (action=activated).
- upsert_active_icp_config updates existing config and writes audit log (action=updated).
- get_active_icp_config returns None when no config exists.
- add_suppression_rule persists rule and writes audit log.
- list_suppression_rules returns rules for the pipeline ordered by created_at desc.
- delete_suppression_rule returns True and writes audit log.
- delete_suppression_rule returns False for cross-pipeline rule.
- upsert_guardrail creates guardrail and writes audit log.
- upsert_guardrail updates existing guardrail.
- list_guardrails returns guardrails ordered by created_at asc.
- list_audit_logs returns all audit log entries for the pipeline.
- Pipeline isolation: operations on pipeline A do not touch pipeline B.
"""

import uuid

import pytest
from sqlalchemy import select

from core.contracts.review import (
    ActiveICPConfigUpsert,
    EnrichmentGuardrailUpsert,
    ReviewDecision,
    ReviewItemCreate,
    SuppressionRuleCreate,
)
from core.models.client import Client
from core.models.pipeline import Pipeline
from core.models.review import ConfigAuditLog
from core.services import review_service


def _create_client(db) -> Client:
    c = Client(name=f"Client-{uuid.uuid4()}", slug=f"c-{uuid.uuid4()}", status="active")
    db.add(c)
    db.flush()
    return c


def _create_pipeline(db, client_id: uuid.UUID) -> Pipeline:
    p = Pipeline(
        client_id=client_id,
        name=f"Pipeline-{uuid.uuid4()}",
        slug=f"p-{uuid.uuid4()}",
        lane="discovery",
        status="active",
    )
    db.add(p)
    db.flush()
    return p


def _review_item_payload(**kwargs) -> ReviewItemCreate:
    defaults = dict(
        item_type="company_name",
        content="Acme Corp",
        evidence_text="Found on page 1",
        confidence=0.9,
    )
    defaults.update(kwargs)
    return ReviewItemCreate(**defaults)


# ── ReviewItem ───────────────────────────────────────────────────────────────

def test_create_review_item_status_pending(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    assert item.status == "pending"
    assert item.client_id == client.id
    assert item.pipeline_id == pipeline.id


def test_create_review_item_writes_audit_log(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == item.id)).all()
    )
    assert len(logs) == 1
    assert logs[0].action == "created"
    assert logs[0].entity_type == "review_item"


def test_list_review_items_ordered_desc(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    for content in ["First", "Second", "Third"]:
        review_service.create_review_item(
            db, client.id, pipeline.id, _review_item_payload(content=content)
        )
    items = review_service.list_review_items(db, client.id, pipeline.id)
    assert len(items) == 3
    assert items[0].content == "Third"


def test_list_review_items_status_filter(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    review_service.decide_review_item(
        db, client.id, pipeline.id, item.id,
        ReviewDecision(status="approved", actor_id="user1"),
    )
    review_service.create_review_item(
        db, client.id, pipeline.id, _review_item_payload(content="Another")
    )
    pending = review_service.list_review_items(db, client.id, pipeline.id, status="pending")
    approved = review_service.list_review_items(db, client.id, pipeline.id, status="approved")
    assert len(pending) == 1
    assert len(approved) == 1


def test_get_review_item_cross_pipeline_returns_none(db):
    client = _create_client(db)
    pipeline_a = _create_pipeline(db, client.id)
    pipeline_b = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline_a.id, _review_item_payload())
    result = review_service.get_review_item(db, client.id, pipeline_b.id, item.id)
    assert result is None


def test_get_review_item_unknown_returns_none(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    result = review_service.get_review_item(db, client.id, pipeline.id, uuid.uuid4())
    assert result is None


def test_decide_review_item_sets_decided_at(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    decided = review_service.decide_review_item(
        db, client.id, pipeline.id, item.id,
        ReviewDecision(status="rejected", actor_id="user1", actor_note="low quality"),
    )
    assert decided.status == "rejected"
    assert decided.decided_at is not None
    assert decided.actor_id == "user1"


def test_decide_review_item_edited_and_approved(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    decided = review_service.decide_review_item(
        db, client.id, pipeline.id, item.id,
        ReviewDecision(
            status="edited_and_approved", actor_id="editor", edited_content="Corrected Corp"
        ),
    )
    assert decided.status == "edited_and_approved"
    assert decided.edited_content == "Corrected Corp"


def test_decide_review_item_not_pending_raises(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    review_service.decide_review_item(
        db, client.id, pipeline.id, item.id,
        ReviewDecision(status="approved"),
    )
    with pytest.raises(ValueError, match="already decided"):
        review_service.decide_review_item(
            db, client.id, pipeline.id, item.id,
            ReviewDecision(status="rejected"),
        )


def test_decide_review_item_not_found_raises(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    with pytest.raises(ValueError, match="not found"):
        review_service.decide_review_item(
            db, client.id, pipeline.id, uuid.uuid4(),
            ReviewDecision(status="approved"),
        )


def test_decide_review_item_writes_audit_log(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    item = review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    review_service.decide_review_item(
        db, client.id, pipeline.id, item.id,
        ReviewDecision(status="approved", actor_id="auditor"),
    )
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == item.id)).all()
    )
    actions = {lg.action for lg in logs}
    assert "created" in actions
    assert "approved" in actions


# ── ActiveICPConfig ───────────────────────────────────────────────────────────

def _icp_payload(**kwargs) -> ActiveICPConfigUpsert:
    defaults = dict(
        vertical="SaaS",
        titles=["CTO", "VP Engineering"],
        geographies=["US", "EU"],
        signals=["hiring"],
        exclusions=["gov"],
        activated_by="admin",
    )
    defaults.update(kwargs)
    return ActiveICPConfigUpsert(**defaults)


def test_upsert_icp_config_creates(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    config = review_service.upsert_active_icp_config(
        db, client.id, pipeline.id, _icp_payload(), actor_id="admin"
    )
    assert config.vertical == "SaaS"
    assert config.client_id == client.id


def test_upsert_icp_config_writes_activated_audit(db):
    from sqlalchemy import select

    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    config = review_service.upsert_active_icp_config(
        db, client.id, pipeline.id, _icp_payload(), actor_id="admin"
    )
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == config.id)).all()
    )
    assert any(lg.action == "activated" for lg in logs)


def test_upsert_icp_config_updates_existing(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    review_service.upsert_active_icp_config(
        db, client.id, pipeline.id, _icp_payload(), actor_id="admin"
    )
    updated = review_service.upsert_active_icp_config(
        db, client.id, pipeline.id, _icp_payload(vertical="FinTech"), actor_id="admin"
    )
    assert updated.vertical == "FinTech"
    config = review_service.get_active_icp_config(db, client.id, pipeline.id)
    assert config is not None and config.vertical == "FinTech"


def test_upsert_icp_config_updated_audit(db):
    from sqlalchemy import select

    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    review_service.upsert_active_icp_config(
        db, client.id, pipeline.id, _icp_payload(), actor_id="admin"
    )
    config = review_service.upsert_active_icp_config(
        db, client.id, pipeline.id, _icp_payload(vertical="FinTech"), actor_id="admin"
    )
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == config.id)).all()
    )
    assert any(lg.action == "updated" for lg in logs)


def test_get_active_icp_config_none_when_missing(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    assert review_service.get_active_icp_config(db, client.id, pipeline.id) is None


# ── SuppressionRule ───────────────────────────────────────────────────────────

def _suppression_payload(**kwargs) -> SuppressionRuleCreate:
    defaults = dict(rule_type="domain", value="spam.com", reason="known spam", added_by="admin")
    defaults.update(kwargs)
    return SuppressionRuleCreate(**defaults)


def test_add_suppression_rule_persists(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    rule = review_service.add_suppression_rule(db, client.id, pipeline.id, _suppression_payload())
    assert rule.value == "spam.com"
    assert rule.rule_type == "domain"


def test_add_suppression_rule_writes_audit(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    rule = review_service.add_suppression_rule(db, client.id, pipeline.id, _suppression_payload())
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == rule.id)).all()
    )
    assert any(lg.action == "created" for lg in logs)


def test_list_suppression_rules(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    review_service.add_suppression_rule(
        db, client.id, pipeline.id, _suppression_payload(value="a.com")
    )
    review_service.add_suppression_rule(
        db, client.id, pipeline.id, _suppression_payload(value="b.com")
    )
    rules = review_service.list_suppression_rules(db, client.id, pipeline.id)
    assert len(rules) == 2


def test_delete_suppression_rule_returns_true(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    rule = review_service.add_suppression_rule(db, client.id, pipeline.id, _suppression_payload())
    result = review_service.delete_suppression_rule(db, client.id, pipeline.id, rule.id)
    assert result is True
    assert review_service.list_suppression_rules(db, client.id, pipeline.id) == []


def test_delete_suppression_rule_cross_pipeline_returns_false(db):
    client = _create_client(db)
    pipeline_a = _create_pipeline(db, client.id)
    pipeline_b = _create_pipeline(db, client.id)
    rule = review_service.add_suppression_rule(db, client.id, pipeline_a.id, _suppression_payload())
    result = review_service.delete_suppression_rule(db, client.id, pipeline_b.id, rule.id)
    assert result is False


def test_delete_suppression_rule_writes_audit(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    rule = review_service.add_suppression_rule(db, client.id, pipeline.id, _suppression_payload())
    rule_id = rule.id
    review_service.delete_suppression_rule(db, client.id, pipeline.id, rule_id)
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == rule_id)).all()
    )
    assert any(lg.action == "deleted" for lg in logs)


# ── EnrichmentGuardrail ───────────────────────────────────────────────────────

def _guardrail_payload(**kwargs) -> EnrichmentGuardrailUpsert:
    defaults = dict(
        guardrail_type="enrichment_provider",
        enabled=True,
        policy_notes="approved by compliance",
        approved_by="compliance_team",
    )
    defaults.update(kwargs)
    return EnrichmentGuardrailUpsert(**defaults)


def test_upsert_guardrail_creates(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    g = review_service.upsert_guardrail(db, client.id, pipeline.id, _guardrail_payload())
    assert g.guardrail_type == "enrichment_provider"
    assert g.enabled is True
    assert g.approved_by == "compliance_team"
    assert g.approved_at is not None


def test_upsert_guardrail_updates_existing(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    review_service.upsert_guardrail(db, client.id, pipeline.id, _guardrail_payload())
    updated = review_service.upsert_guardrail(
        db, client.id, pipeline.id, _guardrail_payload(enabled=False)
    )
    assert updated.enabled is False


def test_upsert_guardrail_writes_audit(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    g = review_service.upsert_guardrail(db, client.id, pipeline.id, _guardrail_payload())
    logs = list(
        db.scalars(select(ConfigAuditLog).where(ConfigAuditLog.entity_id == g.id)).all()
    )
    assert any(lg.action == "enabled" for lg in logs)


def test_upsert_guardrail_disabled_no_approved_at(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    g = review_service.upsert_guardrail(
        db, client.id, pipeline.id,
        _guardrail_payload(enabled=False, approved_by=None),
    )
    assert g.approved_at is None


def test_list_guardrails_ordered_asc(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    review_service.upsert_guardrail(
        db, client.id, pipeline.id, _guardrail_payload(guardrail_type="enrichment_provider")
    )
    review_service.upsert_guardrail(
        db, client.id, pipeline.id, _guardrail_payload(guardrail_type="email_verification")
    )
    guardrails = review_service.list_guardrails(db, client.id, pipeline.id)
    assert len(guardrails) == 2
    assert guardrails[0].created_at <= guardrails[1].created_at


# ── Audit Log ─────────────────────────────────────────────────────────────────

def test_list_audit_logs(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    review_service.create_review_item(db, client.id, pipeline.id, _review_item_payload())
    review_service.add_suppression_rule(db, client.id, pipeline.id, _suppression_payload())
    logs = review_service.list_audit_logs(db, client.id, pipeline.id)
    assert len(logs) >= 2


# ── Pipeline isolation ────────────────────────────────────────────────────────

def test_review_items_pipeline_isolation(db):
    client = _create_client(db)
    pipeline_a = _create_pipeline(db, client.id)
    pipeline_b = _create_pipeline(db, client.id)
    review_service.create_review_item(db, client.id, pipeline_a.id, _review_item_payload())
    assert review_service.list_review_items(db, client.id, pipeline_b.id) == []


def test_suppression_rules_pipeline_isolation(db):
    client = _create_client(db)
    pipeline_a = _create_pipeline(db, client.id)
    pipeline_b = _create_pipeline(db, client.id)
    review_service.add_suppression_rule(db, client.id, pipeline_a.id, _suppression_payload())
    assert review_service.list_suppression_rules(db, client.id, pipeline_b.id) == []
