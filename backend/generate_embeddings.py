"""
BIS Sahayak — Generate Embeddings
Phase 7: RAG / AI Brain

Reads all chunks from PostgreSQL, generates embeddings locally using
sentence-transformers (all-MiniLM-L6-v2), and stores them in chunks.embedding.

- Zero cost — no API key required.
- Skips chunks that already have embeddings (idempotent / safe to rerun).
- Processes in batches for efficiency.

Usage:
    cd bis-sahayak/backend
    venv\\Scripts\\activate
    python generate_embeddings.py

Options (set via env or modify defaults below):
    EMBEDDING_MODEL      Model name (default: all-MiniLM-L6-v2)
    EMBEDDING_DIMENSION  Vector dimension (default: 384)
    EMBEDDING_BATCH_SIZE Chunks per batch (default: 32)
"""

import os
import sys
import logging
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("generate_embeddings")

from sqlalchemy import text
from app.database import engine
from app.rag.embedder import embed_batch, get_embedding_dimension

BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "32"))


def main() -> None:
    logger.info("=" * 60)
    logger.info("BIS Sahayak — Generate Embeddings (Phase 7)")
    logger.info("=" * 60)

    # Validate dimension before doing any work
    logger.info("Loading embedding model to validate dimension...")
    actual_dim = get_embedding_dimension()
    configured_dim = int(os.environ.get("EMBEDDING_DIMENSION", "384"))

    logger.info("Model dimension : %d", actual_dim)
    logger.info("Configured dim  : %d", configured_dim)

    if actual_dim != configured_dim:
        logger.error(
            "Dimension mismatch! Model=%d, EMBEDDING_DIMENSION=%d. "
            "Run migrate_embedding_dim.py first.",
            actual_dim, configured_dim
        )
        sys.exit(1)

    with engine.connect() as conn:
        # Check DB column dimension
        db_dim_row = conn.execute(text(
            "SELECT atttypmod FROM pg_attribute "
            "WHERE attrelid = 'chunks'::regclass AND attname = 'embedding'"
        )).fetchone()
        db_dim = db_dim_row[0] if db_dim_row else None

        if db_dim != actual_dim:
            logger.error(
                "DB column dimension=%s does not match model dimension=%d. "
                "Run migrate_embedding_dim.py first.",
                db_dim, actual_dim
            )
            sys.exit(1)

        logger.info("DB column dimension: %d [OK]", db_dim)

        # Count work to do
        total = conn.execute(text("SELECT COUNT(*) FROM chunks")).scalar() or 0
        already_done = conn.execute(
            text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
        ).scalar() or 0
        to_do = total - already_done
        logger.info("Total chunks: %d | Already embedded: %d | To embed: %d",
                    total, already_done, to_do)

        if to_do == 0:
            logger.info("All chunks already have embeddings. Nothing to do.")
            print("\n[OK] All chunks already embedded.")
            return

        # Fetch chunks needing embeddings
        rows = conn.execute(text(
            "SELECT id, content FROM chunks WHERE embedding IS NULL ORDER BY id"
        )).fetchall()

    # Process in batches
    embedded_count = 0
    failed_count = 0

    for batch_start in range(0, len(rows), BATCH_SIZE):
        batch = rows[batch_start: batch_start + BATCH_SIZE]
        ids = [str(r.id) for r in batch]
        texts = [r.content for r in batch]

        try:
            vectors = embed_batch(texts)
        except Exception as e:
            logger.error("Embedding batch %d failed: %s", batch_start // BATCH_SIZE + 1, e)
            failed_count += len(batch)
            continue

        # Write embeddings back to the database
        with engine.connect() as conn:
            for chunk_id, vector in zip(ids, vectors):
                vec_literal = "[" + ",".join(f"{v:.8f}" for v in vector) + "]"
                conn.execute(text(
                    "UPDATE chunks SET embedding = CAST(:vec AS vector) WHERE id = :id"
                ), {"vec": vec_literal, "id": chunk_id})
            conn.commit()

        embedded_count += len(batch)
        logger.info(
            "Progress: %d / %d chunks embedded",
            embedded_count, to_do
        )

    # Final verification
    with engine.connect() as conn:
        final_count = conn.execute(
            text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")
        ).scalar() or 0

    print()
    print("=" * 60)
    print("  EMBEDDING GENERATION COMPLETE")
    print()
    print(f"  Model used         : {os.environ.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')}")
    print(f"  Dimension          : {actual_dim}")
    print(f"  Chunks embedded    : {embedded_count}")
    print(f"  Chunks failed      : {failed_count}")
    print(f"  Total in DB        : {final_count} / {total}")
    print("=" * 60)

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
