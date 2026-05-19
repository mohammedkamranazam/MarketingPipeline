"""
Acceptance Criteria:
- create_import_batch(db, client_id, pipeline_id, original_name, data, mime_type)
  -> LeadImportBatch: validates pipeline ownership, stores the file, creates a batch
  record with status='pending', creates a PipelineRun and EventOutbox record in the same
  transaction, returns the batch.
- get_import_batch(db, client_id, pipeline_id, batch_id) -> LeadImportBatch | None
  returns the batch only if it belongs to the given client and pipeline.
- list_import_batches(db, client_id, pipeline_id) -> list[LeadImportBatch] in desc order.
- process_import_batch(db, batch_id) parses CSV/XLSX, normalizes each row,
  detects duplicates, persists SeedLeadRow records, updates batch totals and status.
- create_import_batch raises ValueError when pipeline does not belong to client_id.
- Malformed rows (missing required fields) are persisted with status='invalid' and
  non-empty validation_errors.
- Duplicate rows (same normalized first_name+company as a prior row in the batch)
  are persisted with status='duplicate' and is_duplicate=True.
- All pipeline-scoped records include client_id and pipeline_id.
"""

import json
import uuid

from sqlalchemy.orm import Session

from core.contracts.seed_lead import SeedLeadRowInput
from core.models.pipeline import Pipeline
from core.models.run import EventOutbox, PipelineRun
from core.models.seed_lead import LeadImportBatch, SeedLeadRow
from core.services.csv_parser_service import SUPPORTED_TABULAR_MIME_TYPES, parse_tabular
from core.services.seed_lead_service import detect_duplicates, normalize_row
from core.storage.adapter import generate_storage_key, get_storage_adapter


def _get_pipeline(db: Session, client_id: uuid.UUID, pipeline_id: uuid.UUID) -> Pipeline:
    pipeline = db.get(Pipeline, pipeline_id)
    if pipeline is None or pipeline.client_id != client_id:
        raise ValueError(f"Pipeline {pipeline_id} not found for client {client_id}")
    return pipeline


def create_import_batch(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    original_name: str,
    data: bytes,
    mime_type: str,
) -> LeadImportBatch:
    if mime_type not in SUPPORTED_TABULAR_MIME_TYPES:
        raise ValueError(f"Unsupported mime_type: {mime_type}")
    _get_pipeline(db, client_id, pipeline_id)

    storage_key = generate_storage_key(str(pipeline_id), "lead_imports", original_name)
    get_storage_adapter().upload(storage_key, data, mime_type)

    batch = LeadImportBatch(
        client_id=client_id,
        pipeline_id=pipeline_id,
        filename=storage_key.rsplit("/", 1)[-1],
        original_name=original_name,
        mime_type=mime_type,
        size_bytes=len(data),
        storage_key=storage_key,
        status="pending",
    )
    db.add(batch)
    db.flush()

    run = PipelineRun(
        client_id=client_id,
        pipeline_id=pipeline_id,
        run_type="lead_import",
        status="queued",
        trigger="api",
    )
    db.add(run)
    db.flush()

    outbox = EventOutbox(
        event_type="lead_import.uploaded",
        client_id=client_id,
        pipeline_id=pipeline_id,
        run_id=run.id,
        idempotency_key=f"lead_import.uploaded:{batch.id}",
        payload=json.dumps({"batch_id": str(batch.id), "run_id": str(run.id)}),
    )
    db.add(outbox)
    db.commit()
    db.refresh(batch)
    return batch


def get_import_batch(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    batch_id: uuid.UUID,
) -> LeadImportBatch | None:
    batch = db.get(LeadImportBatch, batch_id)
    if batch is None or batch.client_id != client_id or batch.pipeline_id != pipeline_id:
        return None
    return batch


def list_import_batches(
    db: Session,
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
) -> list[LeadImportBatch]:
    from sqlalchemy import select

    stmt = (
        select(LeadImportBatch)
        .where(
            LeadImportBatch.client_id == client_id,
            LeadImportBatch.pipeline_id == pipeline_id,
        )
        .order_by(LeadImportBatch.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def process_import_batch(db: Session, batch_id: uuid.UUID) -> None:
    batch = db.get(LeadImportBatch, batch_id)
    if batch is None:
        raise ValueError(f"LeadImportBatch {batch_id} not found")

    batch.status = "processing"
    db.flush()

    try:
        data = get_storage_adapter().download(batch.storage_key)
        result = parse_tabular(data, batch.mime_type)

        inputs: list[SeedLeadRowInput] = []
        for row in result.rows:
            # map header variants case-insensitively
            lower = {k.lower(): v for k, v in row.items()}
            inputs.append(
                SeedLeadRowInput(
                    first_name=lower.get("first_name") or lower.get("firstname") or "",
                    last_name=lower.get("last_name") or lower.get("lastname") or None,
                    company=lower.get("company") or lower.get("company_name") or None,
                    source=lower.get("source") or None,
                    notes=lower.get("notes") or lower.get("project_context") or None,
                    extra={k: v for k, v in row.items()},
                )
            )

        normalized = [normalize_row(inp) for inp in inputs]
        dup_flags = detect_duplicates(normalized)

        total = len(normalized)
        valid_count = 0
        error_count = 0

        for i, (norm, is_dup) in enumerate(zip(normalized, dup_flags, strict=True)):
            if is_dup:
                status = "duplicate"
                error_count += 1
            elif norm.validation_errors:
                status = "invalid"
                error_count += 1
            else:
                status = "valid"
                valid_count += 1

            raw_row = result.rows[i] if i < len(result.rows) else {}
            db.add(
                SeedLeadRow(
                    batch_id=batch.id,
                    client_id=batch.client_id,
                    pipeline_id=batch.pipeline_id,
                    row_index=i,
                    original_first_name=inputs[i].first_name or None,
                    original_last_name=inputs[i].last_name,
                    original_company=inputs[i].company,
                    original_source=inputs[i].source,
                    original_notes=inputs[i].notes,
                    raw_values=json.dumps(raw_row),
                    normalized_first_name=norm.first_name or None,
                    normalized_last_name=norm.last_name,
                    normalized_company=norm.company,
                    normalized_source=norm.source,
                    status=status,
                    validation_errors=json.dumps(norm.validation_errors),
                    is_duplicate=is_dup,
                )
            )

        batch.total_rows = total
        batch.valid_rows = valid_count
        batch.error_rows = error_count
        batch.status = "completed"
    except Exception as exc:
        batch.status = "failed"
        batch.error_message = str(exc)

    db.commit()
