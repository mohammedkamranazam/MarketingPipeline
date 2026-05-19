"""
Acceptance Criteria:
- create_document(db, client_id, pipeline_id, original_name, data, mime_type) -> Document:
  validates pipeline ownership by client_id, stores the file via StorageAdapter,
  persists a Document record with status='pending', creates a PipelineRun and EventOutbox
  record in the same transaction, and returns the Document.
- get_document(db, client_id, pipeline_id, document_id) -> Document | None returns the
  document only when it belongs to the given pipeline and client.
- list_documents(db, client_id, pipeline_id) -> list[Document] returns all documents
  for the pipeline in created_at descending order.
- process_document(db, document_id) parses the document bytes, saves DocumentPage rows,
  creates DocumentChunk rows via chunking_service, sets status='parsed' (or 'failed').
- create_document raises ValueError when pipeline does not belong to client_id.
- All pipeline-scoped records include client_id and pipeline_id.
"""

import json
import uuid

from sqlalchemy.orm import Session

from core.models.document import Document, DocumentChunk, DocumentPage
from core.models.pipeline import Pipeline
from core.models.run import EventOutbox, PipelineRun
from core.services.chunking_service import chunk_pages
from core.services.parser_service import SUPPORTED_MIME_TYPES, parse_document
from core.storage.adapter import generate_storage_key, get_storage_adapter


def _get_pipeline(db: Session, client_id: uuid.UUID, pipeline_id: uuid.UUID) -> Pipeline:
    pipeline = db.get(Pipeline, pipeline_id)
    if pipeline is None or pipeline.client_id != client_id:
        raise ValueError(f"Pipeline {pipeline_id} not found for client {client_id}")
    return pipeline


def create_document(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    original_name: str,
    data: bytes,
    mime_type: str,
) -> Document:
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise ValueError(f"Unsupported mime_type: {mime_type}")
    _get_pipeline(db, client_id, pipeline_id)

    storage_key = generate_storage_key(str(pipeline_id), "documents", original_name)
    get_storage_adapter().upload(storage_key, data, mime_type)

    doc = Document(
        client_id=client_id,
        pipeline_id=pipeline_id,
        filename=storage_key.rsplit("/", 1)[-1],
        original_name=original_name,
        mime_type=mime_type,
        size_bytes=len(data),
        storage_key=storage_key,
        status="pending",
    )
    db.add(doc)
    db.flush()

    run = PipelineRun(
        client_id=client_id,
        pipeline_id=pipeline_id,
        run_type="document_ingestion",
        status="queued",
        trigger="api",
    )
    db.add(run)
    db.flush()

    outbox = EventOutbox(
        event_type="document.uploaded",
        client_id=client_id,
        pipeline_id=pipeline_id,
        run_id=run.id,
        idempotency_key=f"document.uploaded:{doc.id}",
        payload=json.dumps({"document_id": str(doc.id), "run_id": str(run.id)}),
    )
    db.add(outbox)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Document | None:
    doc = db.get(Document, document_id)
    if doc is None or doc.client_id != client_id or doc.pipeline_id != pipeline_id:
        return None
    return doc


def list_documents(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[Document]:
    from sqlalchemy import select

    stmt = (
        select(Document)
        .where(Document.client_id == client_id, Document.pipeline_id == pipeline_id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def process_document(db: Session, document_id: uuid.UUID) -> None:
    doc = db.get(Document, document_id)
    if doc is None:
        raise ValueError(f"Document {document_id} not found")

    doc.status = "parsing"
    db.flush()

    try:
        data = get_storage_adapter().download(doc.storage_key)
        pages = parse_document(data, doc.mime_type)

        for page in pages:
            db.add(
                DocumentPage(
                    document_id=doc.id,
                    page_number=page.page_number,
                    raw_text=page.raw_text,
                )
            )

        chunks = chunk_pages(pages)
        for chunk in chunks:
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    client_id=doc.client_id,
                    pipeline_id=doc.pipeline_id,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                )
            )

        doc.status = "parsed"
    except Exception as exc:
        doc.status = "failed"
        doc.error_message = str(exc)

    db.commit()
