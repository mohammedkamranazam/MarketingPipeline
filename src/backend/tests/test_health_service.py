from core.services.health import build_health_status
from core.settings import Settings


def test_build_health_status_uses_settings_values() -> None:
    settings = Settings(
        APP_NAME="Test API",
        APP_ENV="test",
        APP_VERSION="9.9.9",
    )

    status = build_health_status(settings)

    assert status.status == "ok"
    assert status.service == "Test API"
    assert status.environment == "test"
    assert status.version == "9.9.9"
