"""
Acceptance Criteria:
- LeadImportBatchResponse includes id, client_id, pipeline_id, filename, original_name,
  mime_type, size_bytes, storage_key, status, total_rows, valid_rows, error_rows,
  error_message, created_at, updated_at.
- SeedLeadRowResponse includes id, batch_id, client_id, pipeline_id, row_index,
  original_first_name, original_last_name, original_company, original_source, original_notes,
  raw_values (str), normalized_first_name, normalized_last_name, normalized_company,
  normalized_source, status, validation_errors (list[str]), is_duplicate, created_at.
- Allowed batch statuses: pending, processing, completed, failed.
- Allowed row statuses: pending, valid, invalid, duplicate.
- SeedLeadRowNormalized is the normalized output of row normalization:
  first_name, last_name (nullable), company (nullable), source (nullable),
  validation_errors (list[str]), is_duplicate.
- No untyped dicts as contract fields.
"""

import json
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BatchStatus = Literal["pending", "processing", "completed", "failed"]
RowStatus = Literal["pending", "valid", "invalid", "duplicate"]


class LeadImportBatchResponse(BaseModel):
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
    total_rows: int
    valid_rows: int
    error_rows: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class SeedLeadRowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    batch_id: uuid.UUID
    client_id: uuid.UUID
    pipeline_id: uuid.UUID
    row_index: int
    original_first_name: str | None
    original_last_name: str | None
    original_company: str | None
    original_source: str | None
    original_notes: str | None
    raw_values: str
    normalized_first_name: str | None
    normalized_last_name: str | None
    normalized_company: str | None
    normalized_source: str | None
    status: str
    validation_errors: list[str]
    is_duplicate: bool
    created_at: datetime

    @field_validator("validation_errors", mode="before")
    @classmethod
    def parse_validation_errors(cls, v: object) -> list[str]:
        if isinstance(v, str):
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        if isinstance(v, list):
            return v
        return []


class SeedLeadRowInput(BaseModel):
    first_name: str = ""
    last_name: str | None = None
    company: str | None = None
    source: str | None = None
    notes: str | None = None
    extra: dict[str, str] = Field(default_factory=dict)


class SeedLeadRowNormalized(BaseModel):
    first_name: str
    last_name: str | None
    company: str | None
    source: str | None
    validation_errors: list[str]
    is_duplicate: bool
