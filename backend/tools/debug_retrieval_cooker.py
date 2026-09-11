"""
BIS Sahayak — Cooker Retrieval Diagnostic Tool (Dev-Only)
Prints for cooker queries:
  - retrieved chunk title
  - document title
  - standard number
  - score
  - first ~300 characters of content
  - content length
"""

import os
import sys
from pathlib import Path

# Load .env if present
_env = Path(".env")
if _env.exists():
    for _line in _env.read_text("utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            k, _, v = _line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, ".")

from app.database import SessionLocal
from app.rag.retriever import retrieve

COOKER_QUERIES = [
    "cooker",
    "pressure cooker",
    "What BIS requirements apply to pressure cookers?",
    "IS 2347",
]


def run_cooker_diagnostic():
    db = SessionLocal()
    print("=" * 85)
    print("BIS SAHAYAK — COOKER RETRIEVAL GRANULARITY & QUALITY DIAGNOSTIC")
    print("=" * 85)

    for q in COOKER_QUERIES:
        print(f"\nQUERY: {q!r}")
        print("-" * 80)
        res = retrieve(q, db, top_k=3)
        if not res.found or not res.chunks:
            print("  NO CHUNKS FOUND!")
            continue

        for idx, c in enumerate(res.chunks, 1):
            clean_snippet = c.content[:300].strip().encode("ascii", "replace").decode("ascii")
            safe_doc_title = c.document_title.encode("ascii", "replace").decode("ascii")
            safe_chunk_title = (c.chunk_title or "None").encode("ascii", "replace").decode("ascii")

            print(f"  [Chunk {idx}]")
            print(f"    Chunk Title:     {safe_chunk_title}")
            print(f"    Document Title:  {safe_doc_title}")
            print(f"    Standard Number: {c.standard_number or 'N/A'}")
            print(f"    Score:           {c.similarity:.4f}")
            print(f"    Content Length:  {len(c.content)} chars")
            print(f"    Snippet (~300 chars):")
            for line in clean_snippet.splitlines():
                print(f"      {line}")
            print()

    db.close()
    print("=" * 85)


if __name__ == "__main__":
    run_cooker_diagnostic()
