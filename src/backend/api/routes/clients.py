"""
Acceptance Criteria:
- POST /clients creates a client and returns 201 with ClientResponse.
- GET /clients returns list of ClientResponse.
- GET /clients/{client_id} returns ClientResponse or 404.
- PATCH /clients/{client_id} applies partial update or returns 404.
- POST /clients/{client_id}/pipelines creates pipeline and returns 201 with PipelineResponse.
- GET /clients/{client_id}/pipelines returns list of PipelineResponse.
- GET /clients/{client_id}/pipelines/{pipeline_id} returns PipelineResponse or 404.
- PATCH /clients/{client_id}/pipelines/{pipeline_id} applies partial update or returns 404.
- All routes delegate business logic to client_service; routes only handle HTTP concerns.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.contracts.client import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    PipelineCreate,
    PipelineResponse,
    PipelineUpdate,
)
from core.db.session import get_db
from core.services import client_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> ClientResponse:
    try:
        client = client_service.create_client(db, payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return ClientResponse.model_validate(client)


@router.get("", response_model=list[ClientResponse])
def list_clients(db: Session = Depends(get_db)) -> list[ClientResponse]:
    return [ClientResponse.model_validate(c) for c in client_service.list_clients(db)]


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: uuid.UUID, db: Session = Depends(get_db)) -> ClientResponse:
    try:
        client = client_service.get_client(db, client_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ClientResponse.model_validate(client)


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: uuid.UUID, payload: ClientUpdate, db: Session = Depends(get_db)
) -> ClientResponse:
    try:
        client = client_service.update_client(db, client_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ClientResponse.model_validate(client)


# ---------------------------------------------------------------------------
# Pipelines under a client
# ---------------------------------------------------------------------------


@router.post(
    "/{client_id}/pipelines",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pipeline(
    client_id: uuid.UUID, payload: PipelineCreate, db: Session = Depends(get_db)
) -> PipelineResponse:
    try:
        pipeline = client_service.create_pipeline(db, client_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return PipelineResponse.model_validate(pipeline)


@router.get("/{client_id}/pipelines", response_model=list[PipelineResponse])
def list_pipelines(
    client_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[PipelineResponse]:
    try:
        client_service.get_client(db, client_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return [
        PipelineResponse.model_validate(p)
        for p in client_service.list_pipelines(db, client_id)
    ]


@router.get("/{client_id}/pipelines/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(
    client_id: uuid.UUID, pipeline_id: uuid.UUID, db: Session = Depends(get_db)
) -> PipelineResponse:
    try:
        pipeline = client_service.get_pipeline(db, client_id, pipeline_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PipelineResponse.model_validate(pipeline)


@router.patch("/{client_id}/pipelines/{pipeline_id}", response_model=PipelineResponse)
def update_pipeline(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    payload: PipelineUpdate,
    db: Session = Depends(get_db),
) -> PipelineResponse:
    try:
        pipeline = client_service.update_pipeline(db, client_id, pipeline_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PipelineResponse.model_validate(pipeline)
