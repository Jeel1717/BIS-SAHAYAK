"""
BIS Sahayak — Retrieval Accuracy Verification & Debug Tool
Development tool only (never exposed to production UI).

Prints for each test query:
  - query
  - top retrieved chunk title
  - document title
  - standard number
  - similarity / final score
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

TEST_CASES = [
    # Cooker natural-language variations
    ("cooker", "Simplified Procedure / Scheme I", True),
    ("pressure cooker", "IS 2347 / Simplified Procedure", True),
    ("cooker certification", "Product Certification / IS 2347", True),
    ("what BIS standard applies to pressure cooker", "IS 2347 / Simplified Procedure", True),
    ("does pressure cooker need BIS certification", "Scheme I QCO / IS 2347", True),
    ("What BIS requirements apply to pressure cookers?", "Simplified Procedure / Scheme I", True),
    ("IS 2347", "Simplified Procedure / IS 2347", True),
    # Non-cooker domain queries
    ("what is HUID", "Hallmarking / HUID", False),
    ("how do I verify hallmarked gold", "Hallmarking / AHC", False),
    ("how can a manufacturer obtain BIS certification", "Product Certification Scheme I", False),
    # Out-of-scope query
    ("how do I bake a chocolate cake", "Out of scope fallback", False),
]


def run_debug_verification():
    db = SessionLocal()
    print("=" * 85)
    print("BIS SAHAYAK — RETRIEVAL ACCURACY & DOMAIN EXPANSION DEBUG TOOL")
    print("=" * 85)

    all_passed = True

    for i, (q, expected_focus, should_have_cooker) in enumerate(TEST_CASES, 1):
        res = retrieve(q, db, top_k=3)
        print(f"\n[Test {i:02d}] Query: {q!r}")
        print(f"  Target Focus: {expected_focus}")

        if q == "how do I bake a chocolate cake":
            if not res.found and len(res.chunks) == 0:
                print("  Result: PASS — 0 chunks returned (safe out-of-scope fallback)")
            else:
                print(f"  Result: FAIL — Expected 0 chunks, got {len(res.chunks)}")
                all_passed = False
            continue

        if not res.found or len(res.chunks) == 0:
            print("  Result: FAIL — No chunks returned!")
            all_passed = False
            continue

        top = res.chunks[0]
        has_cooker = any("cooker" in c.content.lower() or "2347" in c.content for c in res.chunks)

        if should_have_cooker and not has_cooker:
            status = "FAIL (No cooker content in top chunks)"
            all_passed = False
        elif not should_have_cooker and has_cooker:
            status = "FAIL (Cooker content leaked into non-cooker query!)"
            all_passed = False
        else:
            status = "PASS"

        print(f"  Result: {status}")
        print(f"  Top Retrieved Chunk Title: {top.chunk_title or '(Document Level)'}")
        print(f"  Document Title:           {top.document_title}")
        print(f"  Standard Number:          {top.standard_number or 'N/A'}")
        print(f"  Similarity / Score:       {top.similarity:.4f}")
        print(f"  Total Chunks Retrieved:   {len(res.chunks)}")
        print("  Top 3 Excerpts:")
        for idx, c in enumerate(res.chunks, 1):
            clean_excerpt = c.content[:95].strip().replace("\n", " ").encode("ascii", "replace").decode("ascii")
            safe_title = c.document_title[:38].encode("ascii", "replace").decode("ascii")
            print(f"    [{idx}] ({c.similarity:.4f}) {safe_title} -> {clean_excerpt}...")

    print("\n" + "=" * 85)
    if all_passed:
        print("OVERALL RETRIEVAL ACCURACY STATUS: ALL TESTS PASSED!")
    else:
        print("OVERALL RETRIEVAL ACCURACY STATUS: SOME TESTS FAILED!")
    print("=" * 85)
    db.close()


if __name__ == "__main__":
    run_debug_verification()
