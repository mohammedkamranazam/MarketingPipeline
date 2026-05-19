"""
Acceptance Criteria:
- POST /clients/{cid}/pipelines/{pid}/sources creates a source connector (201).
- GET /clients/{cid}/pipelines/{pid}/sources lists connectors; optional ?source_type= filter.
- GET /clients/{cid}/pipelines/{pid}/sources/{id} returns connector or 404.
- PATCH /clients/{cid}/pipelines/{pid}/sources/{id} updates connector or 422.
- DELETE /clients/{cid}/pipelines/{pid}/sources/{id} deletes or 404.
- POST /clients/{cid}/pipelines/{pid}/sources/{id}/test returns SourceTestResult.
- POST /clients/{cid}/pipelines/{pid}/policy-rules creates a policy rule (201).
- GET /clients/{cid}/pipelines/{pid}/policy-rules lists rules.
- DELETE /clients/{cid}/pipelines/{pid}/policy-rules/{rule_id} deletes or 404.
- POST /clients/{cid}/pipelines/{pid}/policy/decide returns PolicyDecisionResponse.
- POST /clients/{cid}/pipelines/{pid}/url-candidates submits URL (201 or 200 if exists).
- GET /clients/{cid}/pipelines/{pid}/url-candidates lists; optional ?status= filter.
- POST /clients/{cid}/pipelines/{pid}/credentials creates credential profile (201).
- GET /clients/{cid}/pipelines/{pid}/credentials lists profiles.
- GET /clients/{cid}/pipelines/{pid}/credentials/{id} returns profile or 404.
- PATCH /clients/{cid}/pipelines/{pid}/credentials/{id} updates profile or 422.
- POST /clients/{cid}/pipelines/{pid}/credentials/{id}/validate runs validation.
- GET /adapters lists all registered adapters.
- POST /adapters registers or updates an adapter.
- All routes delegate to source_service; routes handle HTTP only.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.contracts.source import (
    AdapterRegistryCreate,
    AdapterRegistryResponse,
    CredentialProfileCreate,
    CredentialProfileResponse,
    CredentialProfileUpdate,
    CredentialValidationRunResponse,
    PolicyDecisionRequest,
    PolicyDecisionResponse,
    PolicyRuleCreate,
    PolicyRuleResponse,
    SourceConnectorCreate,
    SourceConnectorResponse,
    SourceConnectorUpdate,
    SourceTestResult,
    URLCandidateCreate,
    URLCandidateResponse,
)
from core.db.session import get_db
from core.services import source_service

_PREFIX = "/clients/{client_id}/pipelines/{pipeline_id}"
router = APIRouter(tags=["source"])


# ── SourceConnectors ──────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/sources",
    response_model=SourceConnectorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_source(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: SourceConnectorCreate,
    db: Session = Depends(get_db),
) -> SourceConnectorResponse:
    c = source_service.create_source_connector(db, client_id, pipeline_id, payload)
    return SourceConnectorResponse.model_validate(c)


@router.get(f"{_PREFIX}/sources", response_model=list[SourceConnectorResponse])
def list_sources(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    source_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[SourceConnectorResponse]:
    connectors = source_service.list_source_connectors(
        db, client_id, pipeline_id, source_type
    )
    return [SourceConnectorResponse.model_validate(c) for c in connectors]


@router.get(f"{_PREFIX}/sources/{{connector_id}}", response_model=SourceConnectorResponse)
def get_source(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SourceConnectorResponse:
    c = source_service.get_source_connector(db, client_id, pipeline_id, connector_id)
    if c is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")
    return SourceConnectorResponse.model_validate(c)


@router.patch(f"{_PREFIX}/sources/{{connector_id}}", response_model=SourceConnectorResponse)
def update_source(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
    payload: SourceConnectorUpdate,
    db: Session = Depends(get_db),
) -> SourceConnectorResponse:
    try:
        c = source_service.update_source_connector(
            db, client_id, pipeline_id, connector_id, payload
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return SourceConnectorResponse.model_validate(c)


@router.delete(f"{_PREFIX}/sources/{{connector_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    deleted = source_service.delete_source_connector(db, client_id, pipeline_id, connector_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")


@router.post(f"{_PREFIX}/sources/{{connector_id}}/test", response_model=SourceTestResult)
def test_source(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    connector_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SourceTestResult:
    return source_service.test_source_connector(db, client_id, pipeline_id, connector_id)


# ── PolicyRules ───────────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/policy-rules",
    response_model=PolicyRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_policy_rule(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: PolicyRuleCreate,
    db: Session = Depends(get_db),
) -> PolicyRuleResponse:
    rule = source_service.create_policy_rule(db, client_id, pipeline_id, payload)
    return PolicyRuleResponse.model_validate(rule)


@router.get(f"{_PREFIX}/policy-rules", response_model=list[PolicyRuleResponse])
def list_policy_rules(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[PolicyRuleResponse]:
    rules = source_service.list_policy_rules(db, client_id, pipeline_id)
    return [PolicyRuleResponse.model_validate(r) for r in rules]


@router.delete(
    f"{_PREFIX}/policy-rules/{{rule_id}}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_policy_rule(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    deleted = source_service.delete_policy_rule(db, client_id, pipeline_id, rule_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Policy rule not found"
        )


@router.post(f"{_PREFIX}/policy/decide", response_model=PolicyDecisionResponse)
def decide_policy(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: PolicyDecisionRequest,
    db: Session = Depends(get_db),
) -> PolicyDecisionResponse:
    return source_service.decide_policy(db, client_id, pipeline_id, payload)


# ── URLCandidates ─────────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/url-candidates",
    response_model=URLCandidateResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_url_candidate(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: URLCandidateCreate,
    db: Session = Depends(get_db),
) -> URLCandidateResponse:
    candidate = source_service.submit_url_candidate(db, client_id, pipeline_id, payload)
    return URLCandidateResponse.model_validate(candidate)


@router.get(f"{_PREFIX}/url-candidates", response_model=list[URLCandidateResponse])
def list_url_candidates(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[URLCandidateResponse]:
    candidates = source_service.list_url_candidates(
        db, client_id, pipeline_id, status_filter
    )
    return [URLCandidateResponse.model_validate(c) for c in candidates]


# ── CredentialProfiles ────────────────────────────────────────────────────────

@router.post(
    f"{_PREFIX}/credentials",
    response_model=CredentialProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_credential(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: CredentialProfileCreate,
    db: Session = Depends(get_db),
) -> CredentialProfileResponse:
    profile = source_service.create_credential_profile(db, client_id, pipeline_id, payload)
    return CredentialProfileResponse.model_validate(profile)


@router.get(f"{_PREFIX}/credentials", response_model=list[CredentialProfileResponse])
def list_credentials(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[CredentialProfileResponse]:
    profiles = source_service.list_credential_profiles(db, client_id, pipeline_id)
    return [CredentialProfileResponse.model_validate(p) for p in profiles]


@router.get(
    f"{_PREFIX}/credentials/{{profile_id}}", response_model=CredentialProfileResponse
)
def get_credential(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CredentialProfileResponse:
    p = source_service.get_credential_profile(db, client_id, pipeline_id, profile_id)
    if p is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Credential profile not found"
        )
    return CredentialProfileResponse.model_validate(p)


@router.patch(
    f"{_PREFIX}/credentials/{{profile_id}}", response_model=CredentialProfileResponse
)
def update_credential(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
    payload: CredentialProfileUpdate,
    db: Session = Depends(get_db),
) -> CredentialProfileResponse:
    try:
        p = source_service.update_credential_profile(
            db, client_id, pipeline_id, profile_id, payload
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return CredentialProfileResponse.model_validate(p)


@router.post(
    f"{_PREFIX}/credentials/{{profile_id}}/validate",
    response_model=CredentialValidationRunResponse,
)
def validate_credential(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CredentialValidationRunResponse:
    try:
        run = source_service.validate_credential(db, client_id, pipeline_id, profile_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return CredentialValidationRunResponse.model_validate(run)


# ── AdapterRegistry ───────────────────────────────────────────────────────────

@router.get("/adapters", response_model=list[AdapterRegistryResponse])
def list_adapters(db: Session = Depends(get_db)) -> list[AdapterRegistryResponse]:
    adapters = source_service.list_adapters(db)
    return [AdapterRegistryResponse.model_validate(a) for a in adapters]


@router.post(
    "/adapters", response_model=AdapterRegistryResponse, status_code=status.HTTP_201_CREATED
)
def register_adapter(
    payload: AdapterRegistryCreate,
    db: Session = Depends(get_db),
) -> AdapterRegistryResponse:
    adapter = source_service.register_adapter(db, payload)
    return AdapterRegistryResponse.model_validate(adapter)
