"""Shared fixtures for Phase 01 tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.main import create_app
from core.db.base import Base
from core.db.session import get_db
from core.models import client as _client_models  # noqa: F401 — registers ORM models
from core.models import crawl as _crawl_models  # noqa: F401 — registers ORM models
from core.models import document as _document_models  # noqa: F401 — registers ORM models
from core.models import extraction as _extraction_models  # noqa: F401 — registers ORM models
from core.models import pipeline as _pipeline_models  # noqa: F401 — registers ORM models
from core.models import review as _review_models  # noqa: F401 — registers ORM models
from core.models import run as _run_models  # noqa: F401 — registers ORM models
from core.models import seed_lead as _seed_lead_models  # noqa: F401 — registers ORM models
from core.models import source as _source_models  # noqa: F401 — registers ORM models

# ---------------------------------------------------------------------------
# In-process SQLite engine for unit/integration tests (no Docker required)
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite://"  # in-memory


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db(engine) -> Session:
    """Provide a transactional, rolled-back Session per test."""
    connection = engine.connect()
    transaction = connection.begin()
    factory = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def api_client(db) -> TestClient:
    """TestClient with DB dependency overridden to use the test session."""
    app = create_app()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
