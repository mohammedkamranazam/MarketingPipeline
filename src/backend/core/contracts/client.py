"""
Acceptance Criteria:
- ClientCreate requires name and slug; both are non-empty strings.
- ClientUpdate allows optional name, slug, status.
- ClientResponse includes id, name, slug, status, created_at, updated_at.
- PipelineCreate requires name, slug, and lane (discovery|seed_enrichment).
- PipelineUpdate allows optional name, slug, lane, status, description.
- PipelineResponse includes all pipeline fields.
- PipelineSettingUpsert carries key and value for setting mutations.
- All IDs are UUIDs.
- All contracts use model_config with from_attributes=True for ORM compatibility.
"""

import re
import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _validate_slug(v: str) -> str:
    if not _SLUG_RE.match(v):
        raise ValueError("slug must be lowercase alphanumeric words separated by hyphens")
    return v


SlugStr = Annotated[str, Field(min_length=1, max_length=100)]


# ---------------------------------------------------------------------------
# Client contracts
# ---------------------------------------------------------------------------


class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: SlugStr
    status: str = Field(default="active", pattern=r"^(active|inactive|suspended)$")

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        return _validate_slug(v)


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: SlugStr | None = None
    status: str | None = Field(default=None, pattern=r"^(active|inactive|suspended)$")

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str | None) -> str | None:
        if v is not None:
            return _validate_slug(v)
        return v


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Pipeline contracts
# ---------------------------------------------------------------------------


class PipelineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: SlugStr
    lane: str = Field(pattern=r"^(discovery|seed_enrichment)$")
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        return _validate_slug(v)


class PipelineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: SlugStr | None = None
    lane: str | None = Field(default=None, pattern=r"^(discovery|seed_enrichment)$")
    status: str | None = Field(default=None, pattern=r"^(active|paused|archived)$")
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str | None) -> str | None:
        if v is not None:
            return _validate_slug(v)
        return v


class PipelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    slug: str
    lane: str
    status: str
    description: str | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Settings contracts
# ---------------------------------------------------------------------------


class SettingUpsert(BaseModel):
    key: str = Field(min_length=1, max_length=255)
    value: str | None = None


class SettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str | None
