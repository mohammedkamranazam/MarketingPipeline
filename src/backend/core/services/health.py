"""
Acceptance Criteria:
- Builds a typed health status from application settings.
- Contains no FastAPI, route, or job orchestration dependencies.
- Returns stable status, service, environment, and version fields.
"""

from core.contracts.health import HealthStatus
from core.settings import Settings


def build_health_status(settings: Settings) -> HealthStatus:
    return HealthStatus(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        version=settings.app_version,
    )
