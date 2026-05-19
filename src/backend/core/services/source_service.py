"""
Acceptance Criteria:
- create_source_connector persists connector scoped to client/pipeline.
- list_source_connectors returns connectors for the pipeline, optional source_type filter.
- get_source_connector returns None when not found or wrong pipeline.
- update_source_connector applies partial update; raises ValueError when not found.
- delete_source_connector removes connector; returns False when not found.
- create_policy_rule persists rule scoped to client/pipeline.
- list_policy_rules returns rules ordered by priority asc.
- delete_policy_rule removes rule; returns False when not found or cross-pipeline.
- decide_policy(client_id, pipeline_id, request) -> PolicyDecisionResponse:
    - Evaluates rules ordered by priority; first match wins.
    - URL matching uses str.startswith on pattern.
    - Entity matching uses entity_id equality.
    - Falls back to "review" when no rule matches.
- submit_url_candidate stores URL; idempotent per (pipeline_id, url).
- list_url_candidates returns candidates for the pipeline, optional status filter.
- test_source_connector returns SourceTestResult (mocked: certified adapters return success,
  uncertified return error).
- create_credential_profile persists profile.
- list_credential_profiles returns profiles for the pipeline.
- get_credential_profile returns None when not found or wrong pipeline.
- update_credential_profile applies partial update.
- validate_credential runs mock validation and updates profile status/timestamps.
- check_preflight raises ValueError when required credential is not active.
- register_adapter persists adapter; updates if adapter_key already exists.
- list_adapters returns all registered adapters.
- All records scoped by client_id and pipeline_id.
"""

import json
import time
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.contracts.source import (
    AdapterRegistryCreate,
    CredentialProfileCreate,
    CredentialProfileUpdate,
    PolicyDecisionRequest,
    PolicyDecisionResponse,
    PolicyRuleCreate,
    SourceConnectorCreate,
    SourceConnectorUpdate,
    SourceTestResult,
    URLCandidateCreate,
)
from core.models.source import (
    AdapterRegistry,
    CredentialProfile,
    CredentialValidationRun,
    PolicyRule,
    SourceConnector,
    URLCandidate,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ── SourceConnector ───────────────────────────────────────────────────────────

def create_source_connector(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: SourceConnectorCreate,
) -> SourceConnector:
    connector = SourceConnector(
        client_id=client_id,
        pipeline_id=pipeline_id,
        source_type=payload.source_type,
        name=payload.name,
        base_url=payload.base_url,
        adapter_key=payload.adapter_key,
        status="active",
        config_json=payload.config_json,
        rate_limit_per_minute=payload.rate_limit_per_minute,
        credential_profile_id=payload.credential_profile_id,
    )
    db.add(connector)
    db.commit()
    db.refresh(connector)
    return connector


def list_source_connectors(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    source_type: str | None = None,
) -> list[SourceConnector]:
    stmt = select(SourceConnector).where(
        SourceConnector.client_id == client_id,
        SourceConnector.pipeline_id == pipeline_id,
    )
    if source_type:
        stmt = stmt.where(SourceConnector.source_type == source_type)
    stmt = stmt.order_by(SourceConnector.created_at.asc())
    return list(db.scalars(stmt).all())


def get_source_connector(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
) -> SourceConnector | None:
    c = db.get(SourceConnector, connector_id)
    if c is None or c.client_id != client_id or c.pipeline_id != pipeline_id:
        return None
    return c


def update_source_connector(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
    payload: SourceConnectorUpdate,
) -> SourceConnector:
    c = get_source_connector(db, client_id, pipeline_id, connector_id)
    if c is None:
        raise ValueError(f"SourceConnector {connector_id} not found for this pipeline")
    if payload.name is not None:
        c.name = payload.name
    if payload.base_url is not None:
        c.base_url = payload.base_url
    if payload.status is not None:
        c.status = payload.status
    if payload.rate_limit_per_minute is not None:
        c.rate_limit_per_minute = payload.rate_limit_per_minute
    if payload.config_json is not None:
        c.config_json = payload.config_json
    if payload.credential_profile_id is not None:
        c.credential_profile_id = payload.credential_profile_id
    db.commit()
    db.refresh(c)
    return c


def delete_source_connector(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
) -> bool:
    c = get_source_connector(db, client_id, pipeline_id, connector_id)
    if c is None:
        return False
    db.delete(c)
    db.commit()
    return True


# ── PolicyRule ────────────────────────────────────────────────────────────────

def create_policy_rule(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: PolicyRuleCreate,
) -> PolicyRule:
    rule = PolicyRule(
        client_id=client_id,
        pipeline_id=pipeline_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        pattern=payload.pattern,
        decision=payload.decision,
        priority=payload.priority,
        reason=payload.reason,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_policy_rules(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[PolicyRule]:
    stmt = (
        select(PolicyRule)
        .where(
            PolicyRule.client_id == client_id,
            PolicyRule.pipeline_id == pipeline_id,
        )
        .order_by(PolicyRule.priority.asc())
    )
    return list(db.scalars(stmt).all())


def delete_policy_rule(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    rule_id: uuid.UUID,
) -> bool:
    rule = db.get(PolicyRule, rule_id)
    if rule is None or rule.client_id != client_id or rule.pipeline_id != pipeline_id:
        return False
    db.delete(rule)
    db.commit()
    return True


def decide_policy(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    request: PolicyDecisionRequest,
) -> PolicyDecisionResponse:
    rules = list_policy_rules(db, client_id, pipeline_id)
    for rule in rules:
        matched = False
        if rule.entity_type == "url_pattern" and request.url and rule.pattern:
            matched = request.url.startswith(rule.pattern)
        elif rule.entity_type == "source" and request.source_connector_id and rule.entity_id:
            matched = rule.entity_id == request.source_connector_id
        elif rule.entity_type == "provider" and request.entity_id and rule.entity_id:
            matched = rule.entity_id == request.entity_id
        if matched:
            return PolicyDecisionResponse(
                decision=rule.decision,  # type: ignore[arg-type]
                matched_rule_id=rule.id,
                reason=rule.reason or f"Matched rule priority={rule.priority}",
            )
    return PolicyDecisionResponse(
        decision="review",
        matched_rule_id=None,
        reason="No matching policy rule; defaulting to review",
    )


# ── URLCandidate ──────────────────────────────────────────────────────────────

def submit_url_candidate(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: URLCandidateCreate,
) -> URLCandidate:
    stmt = select(URLCandidate).where(
        URLCandidate.pipeline_id == pipeline_id,
        URLCandidate.url == payload.url,
    )
    existing = db.scalars(stmt).first()
    if existing:
        return existing

    request = PolicyDecisionRequest(
        operation_type="fetch",
        url=payload.url,
        source_connector_id=payload.source_connector_id,
    )
    policy = decide_policy(db, client_id, pipeline_id, request)

    candidate = URLCandidate(
        client_id=client_id,
        pipeline_id=pipeline_id,
        source_connector_id=payload.source_connector_id,
        url=payload.url,
        status=policy.decision,
        policy_decision=policy.decision,
        discovered_at=_utcnow(),
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def list_url_candidates(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status: str | None = None,
) -> list[URLCandidate]:
    stmt = select(URLCandidate).where(
        URLCandidate.client_id == client_id,
        URLCandidate.pipeline_id == pipeline_id,
    )
    if status:
        stmt = stmt.where(URLCandidate.status == status)
    stmt = stmt.order_by(URLCandidate.created_at.desc())
    return list(db.scalars(stmt).all())


# ── Connector test (mock) ─────────────────────────────────────────────────────

def test_source_connector(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
) -> SourceTestResult:
    connector = get_source_connector(db, client_id, pipeline_id, connector_id)
    if connector is None:
        return SourceTestResult(
            adapter_key="unknown",
            success=False,
            error="Connector not found",
        )
    adapter = db.scalars(
        select(AdapterRegistry).where(AdapterRegistry.adapter_key == connector.adapter_key)
    ).first()
    if adapter is None or not adapter.is_certified:
        return SourceTestResult(
            adapter_key=connector.adapter_key,
            success=False,
            error="Adapter is not certified; cannot execute test",
        )
    start = time.monotonic()
    latency_ms = int((time.monotonic() - start) * 1000) + 5  # simulated 5ms
    return SourceTestResult(
        adapter_key=connector.adapter_key,
        success=True,
        latency_ms=latency_ms,
    )


# ── AdapterRegistry ───────────────────────────────────────────────────────────

def register_adapter(db: Session, payload: AdapterRegistryCreate) -> AdapterRegistry:
    existing = db.scalars(
        select(AdapterRegistry).where(AdapterRegistry.adapter_key == payload.adapter_key)
    ).first()
    if existing:
        existing.display_name = payload.display_name
        existing.source_type = payload.source_type
        existing.terms_url = payload.terms_url
        existing.cost_model = payload.cost_model
        existing.timeout_seconds = payload.timeout_seconds
        existing.retry_class = payload.retry_class
        existing.audit_event_type = payload.audit_event_type
        existing.is_certified = payload.is_certified
        db.commit()
        db.refresh(existing)
        return existing
    adapter = AdapterRegistry(
        adapter_key=payload.adapter_key,
        display_name=payload.display_name,
        source_type=payload.source_type,
        terms_url=payload.terms_url,
        cost_model=payload.cost_model,
        timeout_seconds=payload.timeout_seconds,
        retry_class=payload.retry_class,
        audit_event_type=payload.audit_event_type,
        is_certified=payload.is_certified,
    )
    db.add(adapter)
    db.commit()
    db.refresh(adapter)
    return adapter


def list_adapters(db: Session) -> list[AdapterRegistry]:
    return list(db.scalars(select(AdapterRegistry).order_by(AdapterRegistry.adapter_key)).all())


def get_adapter(db: Session, adapter_key: str) -> AdapterRegistry | None:
    return db.scalars(
        select(AdapterRegistry).where(AdapterRegistry.adapter_key == adapter_key)
    ).first()


# ── CredentialProfile ─────────────────────────────────────────────────────────

def create_credential_profile(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: CredentialProfileCreate,
) -> CredentialProfile:
    profile = CredentialProfile(
        client_id=client_id,
        pipeline_id=pipeline_id,
        name=payload.name,
        adapter_key=payload.adapter_key,
        status="active",
        secret_reference=payload.secret_reference,
        scopes=json.dumps(payload.scopes),
        expires_at=payload.expires_at,
        masked_fingerprint=payload.masked_fingerprint,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_credential_profiles(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[CredentialProfile]:
    stmt = (
        select(CredentialProfile)
        .where(
            CredentialProfile.client_id == client_id,
            CredentialProfile.pipeline_id == pipeline_id,
        )
        .order_by(CredentialProfile.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def get_credential_profile(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
) -> CredentialProfile | None:
    p = db.get(CredentialProfile, profile_id)
    if p is None or p.client_id != client_id or p.pipeline_id != pipeline_id:
        return None
    return p


def update_credential_profile(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: CredentialProfileUpdate,
) -> CredentialProfile:
    p = get_credential_profile(db, client_id, pipeline_id, profile_id)
    if p is None:
        raise ValueError(f"CredentialProfile {profile_id} not found")
    if payload.name is not None:
        p.name = payload.name
    if payload.status is not None:
        p.status = payload.status
    if payload.scopes is not None:
        p.scopes = json.dumps(payload.scopes)
    if payload.expires_at is not None:
        p.expires_at = payload.expires_at
    if payload.masked_fingerprint is not None:
        p.masked_fingerprint = payload.masked_fingerprint
    if payload.rotation_due_at is not None:
        p.rotation_due_at = payload.rotation_due_at
    db.commit()
    db.refresh(p)
    return p


def validate_credential(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
) -> CredentialValidationRun:
    """Mock validation: certified adapters pass; expired credentials fail."""
    profile = get_credential_profile(db, client_id, pipeline_id, profile_id)
    if profile is None:
        raise ValueError(f"CredentialProfile {profile_id} not found")

    now = _utcnow()
    expires = profile.expires_at
    if expires is not None and expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires and expires < now:
        run_status = "failed"
        reason = "Credential has expired"
        profile.status = "expired"
    else:
        run_status = "passed"
        reason = None
        if profile.status in ("expired", "validation_failed"):
            profile.status = "active"

    profile.last_validated_at = now
    profile.next_validation_at = now + timedelta(hours=24)

    run = CredentialValidationRun(
        credential_profile_id=profile.id,
        status=run_status,
        reason=reason,
        checked_scopes=profile.scopes,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def check_preflight(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
) -> None:
    """Raise ValueError when the credential is not healthy for use."""
    profile = get_credential_profile(db, client_id, pipeline_id, profile_id)
    if profile is None:
        raise ValueError(f"CredentialProfile {profile_id} not found")
    if profile.status != "active":
        raise ValueError(
            f"Credential '{profile.name}' is not active (status={profile.status}); "
            "operation blocked"
        )
