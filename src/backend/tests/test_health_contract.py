from core.contracts.health import HealthStatus


def test_health_status_contract_is_typed_and_immutable() -> None:
    status = HealthStatus(
        status="ok",
        service="Marketing Pipeline API",
        environment="local",
        version="0.1.0",
    )

    assert status.model_dump() == {
        "status": "ok",
        "service": "Marketing Pipeline API",
        "environment": "local",
        "version": "0.1.0",
    }
