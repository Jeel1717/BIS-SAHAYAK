"""
BIS Sahayak — Embedding Column Migration
Phase 7: RAG / AI Brain

Safely migrates the chunks.embedding column from its current dimension
to the dimension required by the configured local embedding model.

When to run:
  - BEFORE generate_embeddings.py, if the column dimension doesn't match the model.
  - Safe to run even if no embeddings exist yet (all NULL → no data loss).
  - Idempotent: skips if the column is already the correct dimension.

Usage:
    cd bis-sahayak/backend
    venv\\Scripts\\activate
    python migrate_embedding_dim.py
"""

import os
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Load .env
_env = Path(__file__).parent / ".env"
if _env.exists():
    for _l in _env.read_text("utf-8").splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("="); os.environ.setdefault(k.strip(), v.strip())

from sqlalchemy import text
from app.database import engine


def get_current_column_dim(conn) -> int | None:
    """Return the current dimension of chunks.embedding, or None if column doesn't exist."""
    row = conn.execute(text(
        "SELECT atttypmod FROM pg_attribute "
        "WHERE attrelid = 'chunks'::regclass AND attname = 'embedding'"
    )).fetchone()
    return row[0] if row else None


def get_embedded_count(conn) -> int:
    """Return how many chunks already have a non-NULL embedding."""
    return conn.execute(text(
        "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL"
    )).scalar() or 0


def main() -> None:
    target_dim = int(os.environ.get("EMBEDDING_DIMENSION", "384"))
    print(f"Target embedding dimension (from EMBEDDING_DIMENSION env): {target_dim}")

    with engine.connect() as conn:
        current_dim = get_current_column_dim(conn)
        print(f"Current column dimension in database: {current_dim}")

        if current_dim == target_dim:
            print("[OK] Column is already the correct dimension. No migration needed.")
            return

        # Check for existing embeddings — we refuse to migrate if data would be lost
        embedded = get_embedded_count(conn)
        if embedded > 0:
            print(
                f"[ERROR] {embedded} chunks already have embeddings stored with dimension {current_dim}.\n"
                f"  Migrating would destroy those embeddings.\n"
                f"  Options:\n"
                f"  1. Delete all embeddings first: UPDATE chunks SET embedding = NULL;\n"
                f"  2. Or change EMBEDDING_DIMENSION back to {current_dim} to match current data."
            )
            sys.exit(1)

        print(
            f"[INFO] No embeddings stored yet ({embedded} chunks with NULL).\n"
            f"  Safe to migrate: {current_dim} -> {target_dim} dimensions."
        )

        # Drop and recreate the embedding column with the correct dimension
        print(f"[1/2] Dropping old embedding column (dim={current_dim})...")
        conn.execute(text("ALTER TABLE chunks DROP COLUMN IF EXISTS embedding"))
        conn.commit()

        print(f"[2/2] Adding new embedding column (dim={target_dim})...")
        conn.execute(text(
            f"ALTER TABLE chunks ADD COLUMN embedding vector({target_dim})"
        ))
        conn.commit()

        # Verify
        new_dim = get_current_column_dim(conn)
        print(f"[OK] Migration complete. New column dimension: {new_dim}")


if __name__ == "__main__":
    main()
