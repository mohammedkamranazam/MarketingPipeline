"""
Acceptance Criteria:
- get_engine() returns a SQLAlchemy Engine.
- get_session_factory() returns a sessionmaker.
- get_db() yields a Session that can execute queries and closes after use.
- Calling get_engine() twice returns the same singleton instance.
"""

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from core.db.session import get_db, get_engine, get_session_factory


def test_get_engine_returns_engine() -> None:
    engine = get_engine()
    assert isinstance(engine, Engine)


def test_get_engine_is_singleton() -> None:
    assert get_engine() is get_engine()


def test_get_session_factory_returns_sessionmaker() -> None:
    factory = get_session_factory()
    assert isinstance(factory, sessionmaker)


def test_get_session_factory_is_singleton() -> None:
    assert get_session_factory() is get_session_factory()


def test_get_db_yields_session() -> None:
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)
    try:
        next(gen)
    except StopIteration:
        pass
