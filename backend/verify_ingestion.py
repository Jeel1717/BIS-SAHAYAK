"""Verify Phase 6 ingestion results in the database"""
import os, sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_env = Path(__file__).parent / ".env"
if _env.exists():
    for _l in _env.read_text("utf-8").splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k,_,v = _l.partition("="); os.environ.setdefault(k.strip(), v.strip())

from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    # Document count + titles
    docs = conn.execute(text(
        "SELECT id, title, document_type, source_url FROM documents ORDER BY created_at"
    )).fetchall()

    print(f"DOCUMENTS ({len(docs)} total):")
    for d in docs:
        print(f"  [{d.document_type}] {d.title[:60]}")
        # Sanitize URL for display (don't show if it had credentials, but these are public)
        print(f"    URL: {d.source_url}")

    print()

    # Chunk count per document
    chunk_rows = conn.execute(text(
        """
        SELECT d.title, COUNT(c.id) as chunk_count,
               MIN(c.clause_number) as sample_clause,
               bool_or(c.embedding IS NOT NULL) as has_embedding
        FROM documents d
        JOIN chunks c ON c.document_id = d.id
        GROUP BY d.id, d.title
        ORDER BY d.created_at
        """
    )).fetchall()

    print(f"CHUNKS per document:")
    total_chunks = 0
    for row in chunk_rows:
        print(f"  {row.title[:55]!r}")
        print(f"    chunks={row.chunk_count}, has_embedding={row.has_embedding}")
        total_chunks += row.chunk_count

    print()
    total_docs = conn.execute(text("SELECT COUNT(*) FROM documents")).scalar()
    total_ch = conn.execute(text("SELECT COUNT(*) FROM chunks")).scalar()
    dupes = conn.execute(text(
        "SELECT source_url, COUNT(*) FROM documents GROUP BY source_url HAVING COUNT(*) > 1"
    )).fetchall()

    print(f"SUMMARY:")
    print(f"  Total documents : {total_docs}")
    print(f"  Total chunks    : {total_ch}")
    print(f"  Duplicate docs  : {len(dupes)} (expected: 0)")
    print(f"  Embeddings set  : None (Phase 7)")

    # Sample chunk content
    print()
    sample = conn.execute(text(
        "SELECT content FROM chunks LIMIT 1"
    )).fetchone()
    if sample:
        print(f"SAMPLE CHUNK (first 400 chars):")
        print(f"  {sample.content[:400]}")
