"""
Acceptance Criteria:
- POST /clients/{cid}/pipelines/{pid}/review-items creates a review item (201).
- GET /clients/{cid}/pipelines/{pid}/review-items returns list, with optional ?status= filter.
- GET /clients/{cid}/pipelines/{pid}/review-items/{item_id} returns item or 404.
- POST /clients/{cid}/pipelines/{pid}/review-items/{item_id}/decide applies decision or
  returns 422 when item is not pending or validation fails.
- GET /clients/{cid}/pipelines/{pid}/icp-config returns the active config or 404.
- PUT /clients/{cid}/pipelines/{pid}/icp-config upserts the active config (200/201).
- POST /clients/{cid}/pipelines/{pid}/suppression-rules adds a rule (201).
- GET /clients/{cid}/pipelines/{pid}/suppression-rules lists rules.
- DELETE /clients/{cid}/pipelines/{pid}/suppression-rules/{rule_id} deletes or 404.
- PUT /clients/{cid}/pipelines/{pid}/guardrails upserts a guardrail (200/201).
- GET /clients/{cid}/pipelines/{pid}/guardrails lists guardrails.
- GET /clients/{cid}/pipelines/{pid}/audit-log lists audit entries.
- All routes delegate to review_service; routes handle HTTP only.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.contracts.review import (
    ActiveICPConfigResponse,
    ActiveICPConfigUpsert,
    ConfigAuditLogResponse,
    EnrichmentGuardrailResponse,
    EnrichmentGuardrailUpsert,
    ReviewDecision,
    ReviewItemCreate,
    ReviewItemResponse,
    SuppressionRuleCreate,
    SuppressionRuleResponse,
)
from core.db.session import get_db
from core.services import review_service

_PREFIX = "/clients/{client_id}/pipelines/{pipeline_id}"
router = APIRouter(prefix=_PREFIX, tags=["review"])


# ── ReviewItems ───────────────────────────────────────────────────────────────

@router.post(
    "/review-items",
    response_model=ReviewItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review_item(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: ReviewItemCreate,
    db: Session = Depends(get_db),
) -> ReviewItemResponse:
    item = review_service.create_review_item(db, client_id, pipeline_id, payload)
    return ReviewItemResponse.model_validate(item)


@router.get("/review-items", response_model=list[ReviewItemResponse])
def list_review_items(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[ReviewItemResponse]:
    items = review_service.list_review_items(db, client_id, pipeline_id, status_filter)
    return [ReviewItemResponse.model_validate(i) for i in items]


@router.get("/review-items/{item_id}", response_model=ReviewItemResponse)
def get_review_item(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ReviewItemResponse:
    item = review_service.get_review_item(db, client_id, pipeline_id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review item not found")
    return ReviewItemResponse.model_validate(item)


@router.post("/review-items/{item_id}/decide", response_model=ReviewItemResponse)
def decide_review_item(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    item_id: uuid.UUID,
    decision: ReviewDecision,
    db: Session = Depends(get_db),
) -> ReviewItemResponse:
    try:
        item = review_service.decide_review_item(db, client_id, pipeline_id, item_id, decision)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ReviewItemResponse.model_validate(item)


# ── Active ICP Config ─────────────────────────────────────────────────────────

@router.get("/icp-config", response_model=ActiveICPConfigResponse)
def get_icp_config(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ActiveICPConfigResponse:
    config = review_service.get_active_icp_config(db, client_id, pipeline_id)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active ICP config"
        )
    return ActiveICPConfigResponse.model_validate(config)


@router.put("/icp-config", response_model=ActiveICPConfigResponse)
def upsert_icp_config(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: ActiveICPConfigUpsert,
    db: Session = Depends(get_db),
) -> ActiveICPConfigResponse:
    config = review_service.upsert_active_icp_config(
        db, client_id, pipeline_id, payload, actor_id=payload.activated_by
    )
    return ActiveICPConfigResponse.model_validate(config)


# ── Suppression Rules ─────────────────────────────────────────────────────────

@router.post(
    "/suppression-rules",
    response_model=SuppressionRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_suppression_rule(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: SuppressionRuleCreate,
    db: Session = Depends(get_db),
) -> SuppressionRuleResponse:
    rule = review_service.add_suppression_rule(db, client_id, pipeline_id, payload)
    return SuppressionRuleResponse.model_validate(rule)


@router.get("/suppression-rules", response_model=list[SuppressionRuleResponse])
def list_suppression_rules(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[SuppressionRuleResponse]:
    rules = review_service.list_suppression_rules(db, client_id, pipeline_id)
    return [SuppressionRuleResponse.model_validate(r) for r in rules]


@router.delete("/suppression-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_suppression_rule(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    deleted = review_service.delete_suppression_rule(db, client_id, pipeline_id, rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Suppression rule not found"
        )


# ── Enrichment Guardrails ─────────────────────────────────────────────────────

@router.put("/guardrails", response_model=EnrichmentGuardrailResponse)
def upsert_guardrail(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: EnrichmentGuardrailUpsert,
    db: Session = Depends(get_db),
) -> EnrichmentGuardrailResponse:
    guardrail = review_service.upsert_guardrail(db, client_id, pipeline_id, payload)
    return EnrichmentGuardrailResponse.model_validate(guardrail)


@router.get("/guardrails", response_model=list[EnrichmentGuardrailResponse])
def list_guardrails(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[EnrichmentGuardrailResponse]:
    guardrails = review_service.list_guardrails(db, client_id, pipeline_id)
    return [EnrichmentGuardrailResponse.model_validate(g) for g in guardrails]


# ── Audit Log ─────────────────────────────────────────────────────────────────

@router.get("/audit-log", response_model=list[ConfigAuditLogResponse])
def list_audit_log(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[ConfigAuditLogResponse]:
    logs = review_service.list_audit_logs(db, client_id, pipeline_id)
    return [ConfigAuditLogResponse.model_validate(lg) for lg in logs]
