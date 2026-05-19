"""
Acceptance Criteria:
- DocumentUploadResponse includes document id, pipeline_id, client_id, filename,
  original_name, mime_type, size_bytes, status, created_at.
- DocumentResponse includes all upload fields plus error_message, updated_at.
- DocumentPageResponse includes id, document_id, page_number, raw_text, created_at.
- DocumentChunkResponse includes id, document_id, client_id, pipeline_id, page_number,
  chunk_index, text, char_start, char_end, embedding_model, created_at.
- ExtractedKnowledgeItemResponse includes id, document_id, client_id, pipeline_id,
  item_type, content, evidence_text, evidence_page, confidence, status, created_at, updated_at.
- Allowed document statuses: pending, parsing, parsed, chunked, embedded, failed.
- Allowed knowledge item statuses: pending_review, approved, rejected.
- No untyped dicts as contract fields.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

DocumentStatus = Literal["pending", "parsing", "parsed", "chunked", "embedded", "failed"]
KnowledgeItemStatus = Literal["pending_review", "approved", "rejected"]
KnowledgeItemType = Literal["icp_signal", "enrichment_hint", "suppression_rule", "other"]


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_key: str
    status: str
    created_at: datetime


class DocumentResponse(DocumentUploadResponse):
    error_message: str | None
    updated_at: datetime


class DocumentPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    page_number: int
    raw_text: str
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    page_number: int | None
    chunk_index: int
    text: str
    char_start: int
    char_end: int
    embedding_model: str | None
    created_at: datetime


class ExtractedKnowledgeItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    item_type: str
    content: str
    evidence_text: str
    evidence_page: int | None
    confidence: float
    status: str
    created_at: datetime
    updated_at: datetime
