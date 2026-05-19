"""
Acceptance Criteria:
- create_review_item(db, client_id, pipeline_id, payload) -> ReviewItem persists a new
  pending item and writes a ConfigAuditLog entry.
- list_review_items(db, client_id, pipeline_id, status) -> list[ReviewItem] returns items
  for the pipeline, filtered by status when provided, ordered by created_at desc.
- get_review_item(db, client_id, pipeline_id, item_id) -> ReviewItem | None returns item
  only when it belongs to the given pipeline and client.
- decide_review_item(db, client_id, pipeline_id, item_id, decision) -> ReviewItem applies
  the decision, sets decided_at, writes a ConfigAuditLog entry. Raises ValueError when
  item is not pending.
- upsert_active_icp_config(db, client_id, pipeline_id, payload, actor_id) ->
  ActiveICPConfig inserts or replaces the active config for the pipeline; writes audit log.
- get_active_icp_config(db, client_id, pipeline_id) -> ActiveICPConfig | None.
- add_suppression_rule(db, client_id, pipeline_id, payload) -> SuppressionRule; writes audit.
- list_suppression_rules(db, client_id, pipeline_id) -> list[SuppressionRule].
- delete_suppression_rule(db, client_id, pipeline_id, rule_id) -> bool; writes audit.
- upsert_guardrail(db, client_id, pipeline_id, payload) -> EnrichmentGuardrail; writes audit.
- list_guardrails(db, client_id, pipeline_id) -> list[EnrichmentGuardrail].
- All records scoped by client_id and pipeline_id.
- Pipeline isolation: operations on pipeline A do not touch pipeline B.
"""

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.contracts.review import (
    ActiveICPConfigUpsert,
    EnrichmentGuardrailUpsert,
    ReviewDecision,
    ReviewItemCreate,
    SuppressionRuleCreate,
)
from core.models.review import (
    ActiveICPConfig,
    ConfigAuditLog,
    EnrichmentGuardrail,
    ReviewItem,
    SuppressionRule,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _audit(
    db: Session,
    *,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    actor_id: str | None,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None = None,
    before: object = None,
    after: object = None,
) -> None:
    db.add(
        ConfigAuditLog(
            client_id=client_id,
            pipeline_id=pipeline_id,
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_snapshot=json.dumps(before) if before is not None else None,
            after_snapshot=json.dumps(after) if after is not None else None,
        )
    )


# ── ReviewItem ───────────────────────────────────────────────────────────────

def create_review_item(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: ReviewItemCreate,
) -> ReviewItem:
    item = ReviewItem(
        client_id=client_id,
        pipeline_id=pipeline_id,
        source_document_id=payload.source_document_id,
        source_knowledge_item_id=payload.source_knowledge_item_id,
        item_type=payload.item_type,
        content=payload.content,
        evidence_text=payload.evidence_text,
        evidence_page=payload.evidence_page,
        confidence=payload.confidence,
        status="pending",
    )
    db.add(item)
    db.flush()
    _audit(
        db,
        client_id=client_id,
        pipeline_id=pipeline_id,
        actor_id=None,
        action="created",
        entity_type="review_item",
        entity_id=item.id,
        after={"status": "pending", "item_type": payload.item_type},
    )
    db.commit()
    db.refresh(item)
    return item


def list_review_items(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = None,
) -> list[ReviewItem]:
    stmt = select(ReviewItem).where(
        ReviewItem.client_id == client_id,
        ReviewItem.pipeline_id == pipeline_id,
    )
    if status:
        stmt = stmt.where(ReviewItem.status == status)
    stmt = stmt.order_by(ReviewItem.created_at.desc())
    return list(db.scalars(stmt).all())


def get_review_item(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    item_id: uuid.UUID,
) -> ReviewItem | None:
    item = db.get(ReviewItem, item_id)
    if item is None or item.client_id != client_id or item.pipeline_id != pipeline_id:
        return None
    return item


def decide_review_item(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    item_id: uuid.UUID,
    decision: ReviewDecision,
) -> ReviewItem:
    item = get_review_item(db, client_id, pipeline_id, item_id)
    if item is None:
        raise ValueError(f"ReviewItem {item_id} not found for this pipeline")
    if item.status != "pending":
        raise ValueError(f"ReviewItem {item_id} is already decided (status={item.status})")

    before = {"status": item.status, "content": item.content}
    item.status = decision.status
    item.actor_id = decision.actor_id
    item.actor_note = decision.actor_note
    item.edited_content = decision.edited_content
    item.decided_at = _utcnow()
    db.flush()

    _audit(
        db,
        client_id=client_id,
        pipeline_id=pipeline_id,
        actor_id=decision.actor_id,
        action=decision.status,
        entity_type="review_item",
        entity_id=item.id,
        before=before,
        after={"status": decision.status, "edited_content": decision.edited_content},
    )
    db.commit()
    db.refresh(item)
    return item


# ── ActiveICPConfig ───────────────────────────────────────────────────────────

def upsert_active_icp_config(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: ActiveICPConfigUpsert,
    actor_id: str | None = None,
) -> ActiveICPConfig:
    existing = get_active_icp_config(db, client_id, pipeline_id)
    before = None

    if existing:
        before = {
            "vertical": existing.vertical,
            "titles": existing.titles,
            "signals": existing.signals,
        }
        existing.pipeline_config_version_id = payload.pipeline_config_version_id
        existing.vertical = payload.vertical
        existing.target_company_size_min = payload.target_company_size_min
        existing.target_company_size_max = payload.target_company_size_max
        existing.geographies = json.dumps(payload.geographies)
        existing.titles = json.dumps(payload.titles)
        existing.signals = json.dumps(payload.signals)
        existing.exclusions = json.dumps(payload.exclusions)
        existing.notes = payload.notes
        existing.activated_by = actor_id
        existing.activated_at = _utcnow()
        config = existing
    else:
        config = ActiveICPConfig(
            client_id=client_id,
            pipeline_id=pipeline_id,
            pipeline_config_version_id=payload.pipeline_config_version_id,
            vertical=payload.vertical,
            target_company_size_min=payload.target_company_size_min,
            target_company_size_max=payload.target_company_size_max,
            geographies=json.dumps(payload.geographies),
            titles=json.dumps(payload.titles),
            signals=json.dumps(payload.signals),
            exclusions=json.dumps(payload.exclusions),
            notes=payload.notes,
            activated_by=actor_id,
        )
        db.add(config)

    db.flush()
    _audit(
        db,
        client_id=client_id,
        pipeline_id=pipeline_id,
        actor_id=actor_id,
        action="activated" if not before else "updated",
        entity_type="active_icp_config",
        entity_id=config.id,
        before=before,
        after={"vertical": payload.vertical, "titles": payload.titles},
    )
    db.commit()
    db.refresh(config)
    return config


def get_active_icp_config(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> ActiveICPConfig | None:
    stmt = select(ActiveICPConfig).where(
        ActiveICPConfig.client_id == client_id,
        ActiveICPConfig.pipeline_id == pipeline_id,
    )
    return db.scalars(stmt).first()


# ── SuppressionRule ───────────────────────────────────────────────────────────

def add_suppression_rule(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: SuppressionRuleCreate,
) -> SuppressionRule:
    rule = SuppressionRule(
        client_id=client_id,
        pipeline_id=pipeline_id,
        rule_type=payload.rule_type,
        value=payload.value,
        reason=payload.reason,
        added_by=payload.added_by,
    )
    db.add(rule)
    db.flush()
    _audit(
        db,
        client_id=client_id,
        pipeline_id=pipeline_id,
        actor_id=payload.added_by,
        action="created",
        entity_type="suppression_rule",
        entity_id=rule.id,
        after={"rule_type": payload.rule_type, "value": payload.value},
    )
    db.commit()
    db.refresh(rule)
    return rule


def list_suppression_rules(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[SuppressionRule]:
    stmt = (
        select(SuppressionRule)
        .where(
            SuppressionRule.client_id == client_id,
            SuppressionRule.pipeline_id == pipeline_id,
        )
        .order_by(SuppressionRule.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def delete_suppression_rule(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    rule_id: uuid.UUID,
) -> bool:
    rule = db.get(SuppressionRule, rule_id)
    if rule is None or rule.client_id != client_id or rule.pipeline_id != pipeline_id:
        return False
    _audit(
        db,
        client_id=client_id,
        pipeline_id=pipeline_id,
        actor_id=None,
        action="deleted",
        entity_type="suppression_rule",
        entity_id=rule.id,
        before={"rule_type": rule.rule_type, "value": rule.value},
    )
    db.delete(rule)
    db.commit()
    return True


# ── EnrichmentGuardrail ───────────────────────────────────────────────────────

def upsert_guardrail(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: EnrichmentGuardrailUpsert,
) -> EnrichmentGuardrail:
    stmt = select(EnrichmentGuardrail).where(
        EnrichmentGuardrail.client_id == client_id,
        EnrichmentGuardrail.pipeline_id == pipeline_id,
        EnrichmentGuardrail.guardrail_type == payload.guardrail_type,
    )
    existing = db.scalars(stmt).first()
    before = None
    if existing:
        before = {"enabled": existing.enabled}
        existing.enabled = payload.enabled
        existing.policy_notes = payload.policy_notes
        if payload.enabled and payload.approved_by:
            existing.approved_by = payload.approved_by
            existing.approved_at = _utcnow()
        guardrail = existing
    else:
        guardrail = EnrichmentGuardrail(
            client_id=client_id,
            pipeline_id=pipeline_id,
            guardrail_type=payload.guardrail_type,
            enabled=payload.enabled,
            policy_notes=payload.policy_notes,
            approved_by=payload.approved_by if payload.enabled else None,
            approved_at=_utcnow() if payload.enabled and payload.approved_by else None,
        )
        db.add(guardrail)

    db.flush()
    _audit(
        db,
        client_id=client_id,
        pipeline_id=pipeline_id,
        actor_id=payload.approved_by,
        action="enabled" if payload.enabled else "disabled",
        entity_type="enrichment_guardrail",
        entity_id=guardrail.id,
        before=before,
        after={"guardrail_type": payload.guardrail_type, "enabled": payload.enabled},
    )
    db.commit()
    db.refresh(guardrail)
    return guardrail


def list_guardrails(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[EnrichmentGuardrail]:
    stmt = (
        select(EnrichmentGuardrail)
        .where(
            EnrichmentGuardrail.client_id == client_id,
            EnrichmentGuardrail.pipeline_id == pipeline_id,
        )
        .order_by(EnrichmentGuardrail.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def list_audit_logs(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[ConfigAuditLog]:
    stmt = (
        select(ConfigAuditLog)
        .where(
            ConfigAuditLog.client_id == client_id,
            ConfigAuditLog.pipeline_id == pipeline_id,
        )
        .order_by(ConfigAuditLog.created_at.desc())
    )
    return list(db.scalars(stmt).all())
