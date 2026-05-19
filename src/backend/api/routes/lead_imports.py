"""
Acceptance Criteria:
- POST /clients/{client_id}/pipelines/{pipeline_id}/lead-imports uploads a CSV/XLSX file
  and returns 201 with LeadImportBatchResponse.
- GET /clients/{client_id}/pipelines/{pipeline_id}/lead-imports returns
  list[LeadImportBatchResponse].
- GET /clients/{client_id}/pipelines/{pipeline_id}/lead-imports/{batch_id} returns
  LeadImportBatchResponse or 404.
- GET /clients/{client_id}/pipelines/{pipeline_id}/lead-imports/{batch_id}/rows returns
  list[SeedLeadRowResponse] for the batch.
- Unsupported file types return 422.
- Batch belonging to another pipeline returns 404.
- All routes delegate to lead_import_service; routes handle HTTP only.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.contracts.seed_lead import LeadImportBatchResponse, SeedLeadRowResponse
from core.db.session import get_db
from core.models.seed_lead import SeedLeadRow
from core.services import lead_import_service

router = APIRouter(
    prefix="/clients/{client_id}/pipelines/{pipeline_id}/lead-imports",
    tags=["lead-imports"],
)


@router.post("", response_model=LeadImportBatchResponse, status_code=status.HTTP_201_CREATED)
async def upload_lead_import(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> LeadImportBatchResponse:
    data = await file.read()
    mime_type = file.content_type or "application/octet-stream"
    original_name = file.filename or "upload"
    try:
        batch = lead_import_service.create_import_batch(
            db,
            client_id=client_id,
            pipeline_id=pipeline_id,
            original_name=original_name,
            data=data,
            mime_type=mime_type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return LeadImportBatchResponse.model_validate(batch)


@router.get("", response_model=list[LeadImportBatchResponse])
def list_lead_imports(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[LeadImportBatchResponse]:
    batches = lead_import_service.list_import_batches(
        db, client_id=client_id, pipeline_id=pipeline_id
    )
    return [LeadImportBatchResponse.model_validate(b) for b in batches]


@router.get("/{batch_id}", response_model=LeadImportBatchResponse)
def get_lead_import(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    batch_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> LeadImportBatchResponse:
    batch = lead_import_service.get_import_batch(
        db, client_id=client_id, pipeline_id=pipeline_id, batch_id=batch_id
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
    return LeadImportBatchResponse.model_validate(batch)


@router.get("/{batch_id}/rows", response_model=list[SeedLeadRowResponse])
def list_seed_lead_rows(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    batch_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[SeedLeadRowResponse]:
    from sqlalchemy import select

    batch = lead_import_service.get_import_batch(
        db, client_id=client_id, pipeline_id=pipeline_id, batch_id=batch_id
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
    rows = list(
        db.scalars(
            select(SeedLeadRow)
            .where(SeedLeadRow.batch_id == batch_id)
            .order_by(SeedLeadRow.row_index.asc())
        ).all()
    )
    return [SeedLeadRowResponse.model_validate(r) for r in rows]
