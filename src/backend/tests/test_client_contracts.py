"""
Acceptance Criteria:
- ClientCreate validates required name and slug fields.
- ClientCreate rejects invalid slug format.
- ClientUpdate allows all-None (no-op update).
- PipelineCreate rejects invalid lane values.
- PipelineCreate rejects invalid slug format.
- ClientResponse and PipelineResponse validate from ORM attributes.
"""

import pytest
from pydantic import ValidationError

from core.contracts.client import ClientCreate, ClientUpdate, PipelineCreate, PipelineUpdate


def test_client_create_valid() -> None:
    c = ClientCreate(name="Acme Corp", slug="acme-corp")
    assert c.name == "Acme Corp"
    assert c.slug == "acme-corp"
    assert c.status == "active"


def test_client_create_invalid_slug_uppercase() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="Acme", slug="Acme")


def test_client_create_invalid_slug_spaces() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="Acme", slug="acme corp")


def test_client_create_invalid_slug_trailing_hyphen() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="Acme", slug="acme-")


def test_client_create_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="Acme", slug="acme", status="deleted")


def test_client_create_empty_name() -> None:
    with pytest.raises(ValidationError):
        ClientCreate(name="", slug="acme")


def test_client_update_all_none_is_valid() -> None:
    u = ClientUpdate()
    assert u.name is None
    assert u.slug is None
    assert u.status is None


def test_client_update_invalid_slug() -> None:
    with pytest.raises(ValidationError):
        ClientUpdate(slug="Bad Slug")


def test_pipeline_create_valid_discovery() -> None:
    p = PipelineCreate(name="Discovery 2024", slug="discovery-2024", lane="discovery")
    assert p.lane == "discovery"


def test_pipeline_create_valid_seed_enrichment() -> None:
    p = PipelineCreate(name="Seed Q1", slug="seed-q1", lane="seed_enrichment")
    assert p.lane == "seed_enrichment"


def test_pipeline_create_invalid_lane() -> None:
    with pytest.raises(ValidationError):
        PipelineCreate(name="Bad Lane", slug="bad-lane", lane="other")


def test_pipeline_create_invalid_slug() -> None:
    with pytest.raises(ValidationError):
        PipelineCreate(name="Test", slug="Test Pipeline", lane="discovery")


def test_pipeline_update_all_none_is_valid() -> None:
    u = PipelineUpdate()
    assert u.name is None
    assert u.lane is None
    assert u.status is None


def test_pipeline_update_invalid_status() -> None:
    with pytest.raises(ValidationError):
        PipelineUpdate(status="deleted")
