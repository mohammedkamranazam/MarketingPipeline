"""
Acceptance Criteria:
- POST /clients/{client_id}/pipelines/{pipeline_id}/documents uploads a file and returns
  201 with DocumentUploadResponse.
- GET /clients/{client_id}/pipelines/{pipeline_id}/documents returns list[DocumentResponse].
- GET /clients/{client_id}/pipelines/{pipeline_id}/documents/{document_id} returns
  DocumentResponse or 404.
- GET /clients/{client_id}/pipelines/{pipeline_id}/documents/{document_id}/knowledge
  returns list[ExtractedKnowledgeItemResponse].
- Unsupported file types return 422.
- Document belonging to another pipeline returns 404.
- All routes delegate to document_service; routes handle HTTP only.
"""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.contracts.document import (
    DocumentResponse,
    DocumentUploadResponse,
    ExtractedKnowledgeItemResponse,
)
from core.db.session import get_db
from core.models.document import ExtractedKnowledgeItem
from core.services import document_service

router = APIRouter(
    prefix="/clients/{client_id}/pipelines/{pipeline_id}/documents",
    tags=["documents"],
)


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    data = await file.read()
    mime_type = file.content_type or "application/octet-stream"
    original_name = file.filename or "upload"
    try:
        doc = document_service.create_document(
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
    return DocumentUploadResponse.model_validate(doc)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    docs = document_service.list_documents(db, client_id=client_id, pipeline_id=pipeline_id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    doc = document_service.get_document(
        db, client_id=client_id, pipeline_id=pipeline_id, document_id=document_id
    )
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.get("/{document_id}/knowledge", response_model=list[ExtractedKnowledgeItemResponse])
def list_knowledge_items(
    client_id: uuid.UUID,
    pipeline_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[ExtractedKnowledgeItemResponse]:
    from sqlalchemy import select

    doc = document_service.get_document(
        db, client_id=client_id, pipeline_id=pipeline_id, document_id=document_id
    )
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    items = list(
        db.scalars(
            select(ExtractedKnowledgeItem)
            .where(ExtractedKnowledgeItem.document_id == document_id)
            .order_by(ExtractedKnowledgeItem.created_at.asc())
        ).all()
    )
    return [ExtractedKnowledgeItemResponse.model_validate(it) for it in items]
