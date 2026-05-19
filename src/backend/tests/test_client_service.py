"""
Acceptance Criteria:
- create_client() persists a client and returns it with a UUID id.
- list_clients() returns all persisted clients ordered by name.
- get_client() returns a client by id.
- get_client() raises ValueError for unknown id.
- update_client() applies partial changes.
- update_client() raises ValueError for unknown id.
- create_pipeline() creates a pipeline scoped to the client.
- list_pipelines() returns only pipelines for the given client_id.
- get_pipeline() returns pipeline scoped to client_id+pipeline_id.
- get_pipeline() raises ValueError when pipeline belongs to a different client.
- update_pipeline() applies partial changes scoped by client_id.
- Two pipelines under one client are fully independent (different settings/lane).
"""

import uuid

import pytest

from core.contracts.client import ClientCreate, ClientUpdate, PipelineCreate, PipelineUpdate
from core.services.client_service import (
    create_client,
    create_pipeline,
    get_client,
    get_pipeline,
    list_clients,
    list_pipelines,
    update_client,
    update_pipeline,
)


def test_create_client_persists(db) -> None:
    client = create_client(db, ClientCreate(name="Alpha Corp", slug="alpha-corp"))
    assert client.id is not None
    assert client.name == "Alpha Corp"
    assert client.slug == "alpha-corp"
    assert client.status == "active"


def test_list_clients_ordered_by_name(db) -> None:
    create_client(db, ClientCreate(name="Zebra Inc", slug="zebra-inc"))
    create_client(db, ClientCreate(name="Apple LLC", slug="apple-llc"))
    clients = list_clients(db)
    names = [c.name for c in clients]
    assert names == sorted(names)


def test_get_client_returns_by_id(db) -> None:
    created = create_client(db, ClientCreate(name="Beta Corp", slug="beta-corp"))
    fetched = get_client(db, created.id)
    assert fetched.id == created.id


def test_get_client_raises_for_missing(db) -> None:
    with pytest.raises(ValueError, match="not found"):
        get_client(db, uuid.uuid4())


def test_update_client_applies_partial_changes(db) -> None:
    client = create_client(db, ClientCreate(name="Gamma Corp", slug="gamma-corp"))
    updated = update_client(db, client.id, ClientUpdate(status="inactive"))
    assert updated.status == "inactive"
    assert updated.name == "Gamma Corp"


def test_update_client_raises_for_missing(db) -> None:
    with pytest.raises(ValueError):
        update_client(db, uuid.uuid4(), ClientUpdate(name="Ghost"))


def test_create_pipeline_scoped_to_client(db) -> None:
    client = create_client(db, ClientCreate(name="Delta Corp", slug="delta-corp"))
    pipeline = create_pipeline(
        db,
        client.id,
        PipelineCreate(name="Discovery 2024", slug="discovery-2024", lane="discovery"),
    )
    assert pipeline.client_id == client.id
    assert pipeline.lane == "discovery"


def test_list_pipelines_isolated_per_client(db) -> None:
    c1 = create_client(db, ClientCreate(name="Client One", slug="client-one"))
    c2 = create_client(db, ClientCreate(name="Client Two", slug="client-two"))

    create_pipeline(db, c1.id, PipelineCreate(name="P1", slug="p1", lane="discovery"))
    create_pipeline(db, c1.id, PipelineCreate(name="P2", slug="p2", lane="seed_enrichment"))
    create_pipeline(db, c2.id, PipelineCreate(name="P3", slug="p3", lane="discovery"))

    c1_pipelines = list_pipelines(db, c1.id)
    c2_pipelines = list_pipelines(db, c2.id)

    assert len(c1_pipelines) == 2
    assert len(c2_pipelines) == 1
    assert all(p.client_id == c1.id for p in c1_pipelines)
    assert all(p.client_id == c2.id for p in c2_pipelines)


def test_get_pipeline_cross_client_raises(db) -> None:
    c1 = create_client(db, ClientCreate(name="Owner", slug="owner"))
    c2 = create_client(db, ClientCreate(name="Other", slug="other"))
    pipeline = create_pipeline(
        db, c1.id, PipelineCreate(name="Mine", slug="mine", lane="discovery")
    )

    with pytest.raises(ValueError):
        get_pipeline(db, c2.id, pipeline.id)


def test_update_pipeline_applies_partial_changes(db) -> None:
    client = create_client(db, ClientCreate(name="Epsilon", slug="epsilon"))
    pipeline = create_pipeline(
        db, client.id, PipelineCreate(name="Orig", slug="orig", lane="discovery")
    )
    updated = update_pipeline(
        db, client.id, pipeline.id, PipelineUpdate(status="paused", description="paused for review")
    )
    assert updated.status == "paused"
    assert updated.description == "paused for review"
    assert updated.lane == "discovery"


def test_two_pipelines_under_one_client_are_independent(db) -> None:
    client = create_client(db, ClientCreate(name="TwoLane", slug="two-lane"))
    p1 = create_pipeline(
        db, client.id, PipelineCreate(name="Discovery", slug="discovery", lane="discovery")
    )
    p2 = create_pipeline(
        db, client.id, PipelineCreate(name="Seed", slug="seed", lane="seed_enrichment")
    )
    update_pipeline(db, client.id, p1.id, PipelineUpdate(status="paused"))

    p1_fresh = get_pipeline(db, client.id, p1.id)
    p2_fresh = get_pipeline(db, client.id, p2.id)

    assert p1_fresh.status == "paused"
    assert p2_fresh.status == "active"
    assert p1_fresh.lane != p2_fresh.lane
