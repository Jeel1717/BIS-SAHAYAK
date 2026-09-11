"""Add chunk_title column to existing chunks table safely."""
import os
import sys
from pathlib import Path

_env = Path(__file__).parent.parent.parent / "backend" / ".env"
if not _env.exists():
    _env = Path(__file__).parent / ".env"
if _env.exists():
    for _line in _env.read_text("utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            k, _, v = _line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='chunks' AND column_name='chunk_title'"
    )).fetchone()
    if result:
        print("chunk_title column already exists — no migration needed")
    else:
        conn.execute(text("ALTER TABLE chunks ADD COLUMN chunk_title VARCHAR"))
        conn.commit()
        print("chunk_title column added to chunks table successfully")
