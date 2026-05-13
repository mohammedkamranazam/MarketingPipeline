from fastapi import APIRouter

from core.contracts.health import HealthStatus
from core.services.health import build_health_status
from core.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
def health_check() -> HealthStatus:
    settings = get_settings()
    return build_health_status(settings)
