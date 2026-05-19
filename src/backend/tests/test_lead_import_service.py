"""
Tests for lead_import_service.

Acceptance criteria tested:
- create_import_batch stores file, creates batch with status=pending.
- create_import_batch creates PipelineRun and EventOutbox.
- create_import_batch raises ValueError for unsupported mime_type.
- create_import_batch raises ValueError when pipeline does not belong to client.
- get_import_batch returns None for unknown batch_id.
- get_import_batch returns None when pipeline_id does not match.
- list_import_batches returns only batches for the given pipeline.
- process_import_batch creates SeedLeadRow records with correct status.
- Malformed rows get status=invalid with validation_errors.
- Duplicate rows get status=duplicate with is_duplicate=True.
- Two pipelines under one client do not share batches.
"""

import csv
import io
import uuid

import pytest

from core.models.client import Client
from core.models.pipeline import Pipeline
from core.models.run import EventOutbox, PipelineRun
from core.services import lead_import_service

_CSV_MIME = "text/csv"


def _make_csv(rows: list[dict]) -> bytes:
    if not rows:
        return b"first_name,company\n"
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _create_client(db) -> Client:
    c = Client(name=f"Client-{uuid.uuid4()}", slug=f"c-{uuid.uuid4()}", status="active")
    db.add(c)
    db.flush()
    return c


def _create_pipeline(db, client_id: uuid.UUID, slug: str = "pipe") -> Pipeline:
    p = Pipeline(
        client_id=client_id,
        name=f"P {slug}",
        slug=slug,
        lane="seed_enrichment",
        status="active",
    )
    db.add(p)
    db.flush()
    return p


def test_create_batch_returns_pending(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    data = _make_csv([{"first_name": "Alice", "company": "Acme"}])
    batch = lead_import_service.create_import_batch(
        db, client.id, pipeline.id, "leads.csv", data, _CSV_MIME
    )
    assert batch.status == "pending"
    assert batch.original_name == "leads.csv"
    assert batch.client_id == client.id
    assert batch.pipeline_id == pipeline.id


def test_create_batch_creates_run_and_outbox(db):
    from sqlalchemy import select

    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    data = _make_csv([{"first_name": "Alice", "company": "Acme"}])
    batch = lead_import_service.create_import_batch(
        db, client.id, pipeline.id, "leads.csv", data, _CSV_MIME
    )
    run = db.scalars(
        select(PipelineRun).where(
            PipelineRun.pipeline_id == pipeline.id,
            PipelineRun.run_type == "lead_import",
        )
    ).first()
    assert run is not None
    outbox = db.scalars(
        select(EventOutbox).where(EventOutbox.event_type == "lead_import.uploaded")
    ).first()
    assert outbox is not None
    assert str(batch.id) in outbox.payload


def test_create_batch_unsupported_mime_raises(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    with pytest.raises(ValueError, match="Unsupported mime_type"):
        lead_import_service.create_import_batch(
            db, client.id, pipeline.id, "file.pdf", b"data", "application/pdf"
        )


def test_create_batch_wrong_client_raises(db):
    client = _create_client(db)
    other = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    data = _make_csv([{"first_name": "Alice", "company": "Acme"}])
    with pytest.raises(ValueError, match="not found"):
        lead_import_service.create_import_batch(
            db, other.id, pipeline.id, "leads.csv", data, _CSV_MIME
        )


def test_get_batch_not_found_returns_none(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    assert lead_import_service.get_import_batch(db, client.id, pipeline.id, uuid.uuid4()) is None


def test_get_batch_wrong_pipeline_returns_none(db):
    client = _create_client(db)
    p1 = _create_pipeline(db, client.id, "x1")
    p2 = _create_pipeline(db, client.id, "x2")
    data = _make_csv([{"first_name": "Alice", "company": "Acme"}])
    batch = lead_import_service.create_import_batch(
        db, client.id, p1.id, "leads.csv", data, _CSV_MIME
    )
    assert lead_import_service.get_import_batch(db, client.id, p2.id, batch.id) is None


def test_list_batches_scoped_to_pipeline(db):
    client = _create_client(db)
    p1 = _create_pipeline(db, client.id, "y1")
    p2 = _create_pipeline(db, client.id, "y2")
    data = _make_csv([{"first_name": "Alice", "company": "Acme"}])
    lead_import_service.create_import_batch(db, client.id, p1.id, "a.csv", data, _CSV_MIME)
    lead_import_service.create_import_batch(db, client.id, p2.id, "b.csv", data, _CSV_MIME)
    assert len(lead_import_service.list_import_batches(db, client.id, p1.id)) == 1
    assert len(lead_import_service.list_import_batches(db, client.id, p2.id)) == 1


def test_process_batch_valid_rows(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    data = _make_csv([
        {"first_name": "Alice", "company": "Acme"},
        {"first_name": "Bob", "company": "Beta"},
    ])
    batch = lead_import_service.create_import_batch(
        db, client.id, pipeline.id, "leads.csv", data, _CSV_MIME
    )
    lead_import_service.process_import_batch(db, batch.id)
    db.refresh(batch)
    assert batch.status == "completed"
    assert batch.total_rows == 2
    assert batch.valid_rows == 2
    assert batch.error_rows == 0
    assert len(batch.rows) == 2
    assert all(r.status == "valid" for r in batch.rows)


def test_process_batch_invalid_row_missing_first_name(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    data = _make_csv([
        {"first_name": "", "company": "Acme"},
    ])
    batch = lead_import_service.create_import_batch(
        db, client.id, pipeline.id, "leads.csv", data, _CSV_MIME
    )
    lead_import_service.process_import_batch(db, batch.id)
    db.refresh(batch)
    assert batch.error_rows == 1
    row = batch.rows[0]
    assert row.status == "invalid"
    assert row.validation_errors != "[]"


def test_process_batch_duplicate_rows(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    data = _make_csv([
        {"first_name": "Alice", "company": "Acme"},
        {"first_name": "Alice", "company": "Acme"},
    ])
    batch = lead_import_service.create_import_batch(
        db, client.id, pipeline.id, "leads.csv", data, _CSV_MIME
    )
    lead_import_service.process_import_batch(db, batch.id)
    db.refresh(batch)
    statuses = [r.status for r in batch.rows]
    assert "valid" in statuses
    assert "duplicate" in statuses


def test_two_pipelines_do_not_share_batches(db):
    client = _create_client(db)
    p1 = _create_pipeline(db, client.id, "z1")
    p2 = _create_pipeline(db, client.id, "z2")
    data = _make_csv([{"first_name": "Alice", "company": "Acme"}])
    lead_import_service.create_import_batch(db, client.id, p1.id, "a.csv", data, _CSV_MIME)
    assert lead_import_service.list_import_batches(db, client.id, p2.id) == []
