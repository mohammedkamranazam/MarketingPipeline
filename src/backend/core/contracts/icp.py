"""
Acceptance Criteria:
- ICPExtractionResult groups a list of ICPSignal items extracted from a document.
- ICPSignal has item_type, content, evidence_text, evidence_page (nullable), confidence (float).
- item_type is constrained to known signal types: icp_signal, enrichment_hint,
  suppression_rule, other.
- confidence must be in [0.0, 1.0].
- evidence_text must be non-empty (signals must cite source text).
- ICPExtractionRequest carries document_id, pipeline_id, client_id, and chunk_texts
  for the extractor to operate on.
- No untyped dicts as contract fields.
"""

import uuid

from pydantic import BaseModel, Field, field_validator


class ICPSignal(BaseModel):
    item_type: str = Field(default="icp_signal")
    content: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    evidence_page: int | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class ICPExtractionResult(BaseModel):
    document_id: uuid.UUID
    pipeline_id: uuid.UUID
    client_id: uuid.UUID
    signals: list[ICPSignal] = Field(default_factory=list)


class ICPExtractionRequest(BaseModel):
    document_id: uuid.UUID
    pipeline_id: uuid.UUID
    client_id: uuid.UUID
    chunk_texts: list[str] = Field(default_factory=list)

    @field_validator("chunk_texts")
    @classmethod
    def chunks_non_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("chunk_texts must not be empty")
        return v
