"""
Acceptance Criteria:
- get_engine() returns a SQLAlchemy Engine configured from settings DATABASE_URL.
- get_session_factory() returns a sessionmaker bound to the engine.
- get_db() yields a Session and closes it after use.
- Engine uses psycopg (sync) driver.
- Engine and session factory are not recreated on every call (module-level singletons).
"""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.settings import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    factory = get_session_factory()
    session: Session = factory()
    try:
        yield session
    finally:
        session.close()
