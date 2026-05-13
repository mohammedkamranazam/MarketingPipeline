"""
Acceptance Criteria:
- Defines the typed backend contract for service health responses.
- Can be imported by API, tests, and future job orchestration without API dependencies.
"""

from pydantic import BaseModel, ConfigDict


class HealthStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    service: str
    environment: str
    version: str
