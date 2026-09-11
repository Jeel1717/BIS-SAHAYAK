"""
BIS Sahayak — Database Engine & Session
Phase 5: Database layer

Provides:
  - engine        : SQLAlchemy sync engine (psycopg3 driver)
  - SessionLocal  : session factory
  - Base          : declarative base for all models
  - get_db()      : FastAPI dependency that yields a DB session

SECURITY: DATABASE_URL is read from the environment.
          It is never printed, logged, or returned in any response.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ── 1. Load .env (only in non-production environments) ───────────────────────
#    In production the platform injects env vars directly — no .env file.

_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists() and os.environ.get("APP_ENV", "development") != "production":
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip())

# ── 2. Read DATABASE_URL ──────────────────────────────────────────────────────

_database_url = os.environ.get("DATABASE_URL", "")
if not _database_url:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Add it to backend/.env (see backend/.env.example)."
    )

# SQLAlchemy 2.x uses the 'postgresql+psycopg' dialect for psycopg3.
# If the URL starts with 'postgresql://' (psycopg2 style), convert it.
if _database_url.startswith("postgresql://") and "+psycopg" not in _database_url:
    _database_url = _database_url.replace("postgresql://", "postgresql+psycopg://", 1)

# ── 3. Embedding dimension ────────────────────────────────────────────────────

EMBEDDING_DIMENSION: int = int(os.environ.get("EMBEDDING_DIMENSION", "1536"))

from sqlalchemy.pool import NullPool

import socket
from urllib.parse import urlparse

_parsed_host = urlparse(_database_url).hostname
_hostaddr = None
if _parsed_host:
    try:
        _hostaddr = socket.gethostbyname(_parsed_host)
    except Exception:
        _hostaddr = None

_connect_args = {
    "prepare_threshold": None,
    "connect_timeout": 10,
}
if _hostaddr:
    _connect_args["hostaddr"] = _hostaddr

engine = create_engine(
    _database_url,
    poolclass=NullPool,
    connect_args=_connect_args,
    echo=False,  # Set to True only for SQL debugging; NEVER in production.
)

# ── 5. Session factory ────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ── 6. Declarative base (all models inherit from this) ────────────────────────


class Base(DeclarativeBase):
    pass


# ── 7. FastAPI dependency — yields a DB session per request ───────────────────


def get_db():
    """
    FastAPI dependency.

    Usage in a route:
        from app.database import get_db
        from sqlalchemy.orm import Session
        from fastapi import Depends

        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
