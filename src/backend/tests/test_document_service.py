"""
Tests for document_service.

Acceptance criteria tested:
- create_document stores file, creates Document with status=pending.
- create_document creates PipelineRun and EventOutbox in same transaction.
- create_document raises ValueError for unsupported mime_type.
- create_document raises ValueError when pipeline does not belong to client.
- get_document returns None when document_id does not exist.
- get_document returns None when pipeline_id does not match.
- list_documents returns only documents for the given pipeline.
- process_document sets status=parsed and creates DocumentPage/DocumentChunk rows.
- process_document sets status=failed when storage key is missing.
- Two pipelines under one client do not share documents.
"""

import uuid

import pytest

from core.models.client import Client
from core.models.pipeline import Pipeline
from core.models.run import EventOutbox, PipelineRun
from core.services import document_service

_TXT_MIME = "text/plain"
_TXT_DATA = b"Hello document content for testing."


def _create_client(db) -> Client:
    c = Client(name=f"Client-{uuid.uuid4()}", slug=f"client-{uuid.uuid4()}", status="active")
    db.add(c)
    db.flush()
    return c


def _create_pipeline(db, client_id: uuid.UUID, slug: str = "pipe") -> Pipeline:
    p = Pipeline(
        client_id=client_id,
        name=f"Pipeline {slug}",
        slug=slug,
        lane="discovery",
        status="active",
    )
    db.add(p)
    db.flush()
    return p


def test_create_document_returns_pending(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    doc = document_service.create_document(
        db,
        client_id=client.id,
        pipeline_id=pipeline.id,
        original_name="test.txt",
        data=_TXT_DATA,
        mime_type=_TXT_MIME,
    )
    assert doc.status == "pending"
    assert doc.original_name == "test.txt"
    assert doc.size_bytes == len(_TXT_DATA)
    assert doc.client_id == client.id
    assert doc.pipeline_id == pipeline.id


def test_create_document_creates_pipeline_run_and_outbox(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    doc = document_service.create_document(
        db,
        client_id=client.id,
        pipeline_id=pipeline.id,
        original_name="test.txt",
        data=_TXT_DATA,
        mime_type=_TXT_MIME,
    )
    from sqlalchemy import select

    run = db.scalars(
        select(PipelineRun).where(
            PipelineRun.pipeline_id == pipeline.id,
            PipelineRun.run_type == "document_ingestion",
        )
    ).first()
    assert run is not None

    outbox = db.scalars(
        select(EventOutbox).where(EventOutbox.event_type == "document.uploaded")
    ).first()
    assert outbox is not None
    assert str(doc.id) in outbox.payload


def test_create_document_unsupported_mime_raises(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    with pytest.raises(ValueError, match="Unsupported mime_type"):
        document_service.create_document(
            db,
            client_id=client.id,
            pipeline_id=pipeline.id,
            original_name="file.zip",
            data=b"data",
            mime_type="application/zip",
        )


def test_create_document_wrong_client_raises(db):
    client = _create_client(db)
    other_client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    with pytest.raises(ValueError, match="not found"):
        document_service.create_document(
            db,
            client_id=other_client.id,
            pipeline_id=pipeline.id,
            original_name="test.txt",
            data=_TXT_DATA,
            mime_type=_TXT_MIME,
        )


def test_get_document_not_found_returns_none(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    result = document_service.get_document(db, client.id, pipeline.id, uuid.uuid4())
    assert result is None


def test_get_document_wrong_pipeline_returns_none(db):
    client = _create_client(db)
    p1 = _create_pipeline(db, client.id, "p1")
    p2 = _create_pipeline(db, client.id, "p2")
    doc = document_service.create_document(
        db, client.id, p1.id, "test.txt", _TXT_DATA, _TXT_MIME
    )
    result = document_service.get_document(db, client.id, p2.id, doc.id)
    assert result is None


def test_list_documents_scoped_to_pipeline(db):
    client = _create_client(db)
    p1 = _create_pipeline(db, client.id, "pa")
    p2 = _create_pipeline(db, client.id, "pb")
    document_service.create_document(db, client.id, p1.id, "a.txt", _TXT_DATA, _TXT_MIME)
    document_service.create_document(db, client.id, p2.id, "b.txt", _TXT_DATA, _TXT_MIME)
    docs_p1 = document_service.list_documents(db, client.id, p1.id)
    docs_p2 = document_service.list_documents(db, client.id, p2.id)
    assert len(docs_p1) == 1
    assert len(docs_p2) == 1
    assert docs_p1[0].pipeline_id == p1.id
    assert docs_p2[0].pipeline_id == p2.id


def test_process_document_creates_pages_and_chunks(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    doc = document_service.create_document(
        db, client.id, pipeline.id, "test.txt", _TXT_DATA, _TXT_MIME
    )
    document_service.process_document(db, doc.id)
    db.refresh(doc)
    assert doc.status == "parsed"
    assert len(doc.pages) == 1
    assert len(doc.chunks) >= 1


def test_process_document_failed_on_missing_storage_key(db):
    client = _create_client(db)
    pipeline = _create_pipeline(db, client.id)
    doc = document_service.create_document(
        db, client.id, pipeline.id, "test.txt", _TXT_DATA, _TXT_MIME
    )
    # corrupt the storage key so download fails
    doc.storage_key = "nonexistent/path/file.txt"
    db.flush()

    document_service.process_document(db, doc.id)
    db.refresh(doc)
    assert doc.status == "failed"
    assert doc.error_message is not None


def test_two_pipelines_do_not_share_documents(db):
    client = _create_client(db)
    p1 = _create_pipeline(db, client.id, "q1")
    p2 = _create_pipeline(db, client.id, "q2")
    document_service.create_document(db, client.id, p1.id, "a.txt", _TXT_DATA, _TXT_MIME)
    assert document_service.list_documents(db, client.id, p2.id) == []
