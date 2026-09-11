"""
BIS Sahayak — Create Tables & Verify Schema
Phase 5: Database Schema

What this script does:
  1. Enables the pgvector extension in Supabase (if not already enabled).
  2. Creates all four tables using SQLAlchemy's Base.metadata.create_all().
  3. Verifies every table exists.
  4. Verifies chunks.embedding uses the pgvector type.
  5. Reports results WITHOUT exposing DATABASE_URL or credentials.
"""

import sys
import os
from pathlib import Path

# ── Force UTF-8 output on Windows ────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── Load .env ─────────────────────────────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ── Imports (after env is loaded) ─────────────────────────────────────────────
from sqlalchemy import text, inspect
from app.database import engine, Base
import app.models  # noqa: F401 — registers all four models

EXPECTED_TABLES = {"documents", "chunks", "chat_sessions", "chat_messages"}

# ── Step 1: Enable pgvector extension ────────────────────────────────────────
print("[1/4] Enabling pgvector extension (safe to run if already enabled)...")
try:
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    print("      [OK] pgvector extension ready")
except Exception as e:
    print(f"      [FAIL] Could not enable pgvector: {type(e).__name__}: {e}")
    print("        If you are on Supabase, enable it via:")
    print("        Dashboard -> Database -> Extensions -> vector")
    sys.exit(1)

# ── Step 2: Create all tables ─────────────────────────────────────────────────
print()
print("[2/4] Creating tables (CREATE TABLE IF NOT EXISTS)...")
try:
    Base.metadata.create_all(bind=engine)
    print("      [OK] Base.metadata.create_all() completed")
except Exception as e:
    safe = str(e)
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        safe = safe.replace(db_url, "[DATABASE_URL_REDACTED]")
    print(f"      [FAIL] {type(e).__name__}: {safe}")
    sys.exit(1)

# ── Step 3: Verify all four tables exist ──────────────────────────────────────
print()
print("[3/4] Verifying tables exist...")
inspector = inspect(engine)
existing = set(inspector.get_table_names())
all_ok = True

for table in sorted(EXPECTED_TABLES):
    if table in existing:
        print(f"      [OK]   {table}")
    else:
        print(f"      [MISS] {table}  <- MISSING")
        all_ok = False

if not all_ok:
    print()
    print("[ERROR] One or more tables are missing.")
    sys.exit(1)

# ── Step 4: Verify chunks.embedding is a pgvector column ─────────────────────
print()
print("[4/4] Verifying chunks.embedding column type...")

with engine.connect() as conn:
    row = conn.execute(
        text(
            """
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'chunks'
              AND column_name = 'embedding'
            LIMIT 1;
            """
        )
    ).fetchone()

if row is None:
    print("      [FAIL] chunks.embedding column not found")
    sys.exit(1)

data_type, udt_name = row
print(f"      data_type : {data_type}")
print(f"      udt_name  : {udt_name}")

if udt_name == "vector":
    print("      [OK]   chunks.embedding confirmed as pgvector 'vector' type")
else:
    print(f"      [FAIL] Unexpected type: {udt_name!r} -- expected 'vector'")
    sys.exit(1)

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  PHASE 5 DATABASE SCHEMA -- ALL CHECKS PASSED")
print()
print("  Tables created:")
for t in sorted(EXPECTED_TABLES):
    print(f"    - {t}")
print()
print("  pgvector embedding column: verified")
print(f"  Embedding dimension: {os.environ.get('EMBEDDING_DIMENSION', '1536')}")
print("=" * 55)
