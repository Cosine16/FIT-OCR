"""SQLAlchemy database engine and session management."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL_DEFAULT = "sqlite:///data/fitocr.db"


def get_engine(database_url: str | None = None):
    """Create a SQLAlchemy engine.

    Defaults to SQLite at data/fitocr.db. Swap DATABASE_URL for PostgreSQL.
    """
    url = database_url or DATABASE_URL_DEFAULT
    connect_args: dict = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        # Ensure data dir exists
        db_path = Path(url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    return create_engine(url, connect_args=connect_args, echo=False)


_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def init_db(database_url: str | None = None):
    """Initialize database engine and create all tables."""
    global _engine, _SessionLocal
    _engine = get_engine(database_url)
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

    from server.infrastructure.models import Base

    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    """Get a new database session. Caller must close it."""
    if _SessionLocal is None:
        init_db()
    assert _SessionLocal is not None
    return _SessionLocal()
