"""
Acceptance Criteria:
- create_client() inserts a new client and returns the ORM model.
- list_clients() returns all clients ordered by name.
- get_client() returns the client by id or raises ValueError if not found.
- update_client() applies partial updates and returns the updated model or raises ValueError.
- create_pipeline() inserts a pipeline scoped to a client_id and returns the ORM model.
- list_pipelines() returns pipelines for a given client_id ordered by name.
- get_pipeline() returns the pipeline scoped to client_id+pipeline_id or raises ValueError.
- update_pipeline() applies partial updates scoped to client_id+pipeline_id.
- All queries are scoped by client_id where applicable.
- Pipeline queries are scoped by both client_id and pipeline_id.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.contracts.client import ClientCreate, ClientUpdate, PipelineCreate, PipelineUpdate
from core.models.client import Client
from core.models.pipeline import Pipeline


def create_client(db: Session, payload: ClientCreate) -> Client:
    client = Client(
        name=payload.name,
        slug=payload.slug,
        status=payload.status,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(db: Session) -> list[Client]:
    return list(db.scalars(select(Client).order_by(Client.name)))


def get_client(db: Session, client_id: uuid.UUID) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise ValueError(f"Client {client_id} not found")
    return client


def update_client(db: Session, client_id: uuid.UUID, payload: ClientUpdate) -> Client:
    client = get_client(db, client_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


def create_pipeline(db: Session, client_id: uuid.UUID, payload: PipelineCreate) -> Pipeline:
    get_client(db, client_id)  # validate client exists
    pipeline = Pipeline(
        client_id=client_id,
        name=payload.name,
        slug=payload.slug,
        lane=payload.lane,
        description=payload.description,
    )
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline


def list_pipelines(db: Session, client_id: uuid.UUID) -> list[Pipeline]:
    return list(
        db.scalars(
            select(Pipeline).where(Pipeline.client_id == client_id).order_by(Pipeline.name)
        )
    )


def get_pipeline(db: Session, client_id: uuid.UUID, pipeline_id: uuid.UUID) -> Pipeline:
    pipeline = db.scalar(
        select(Pipeline).where(
            Pipeline.id == pipeline_id, Pipeline.client_id == client_id
        )
    )
    if pipeline is None:
        raise ValueError(f"Pipeline {pipeline_id} not found for client {client_id}")
    return pipeline


def update_pipeline(
    db: Session, client_id: uuid.UUID, pipeline_id: uuid.UUID, payload: PipelineUpdate
) -> Pipeline:
    pipeline = get_pipeline(db, client_id, pipeline_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(pipeline, field, value)
    db.commit()
    db.refresh(pipeline)
    return pipeline
