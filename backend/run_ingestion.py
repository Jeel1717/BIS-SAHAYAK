"""
BIS Sahayak — Run Ingestion (Chapter 14)

Usage:
    cd bis-sahayak/backend
    .\\venv\\Scripts\\python.exe run_ingestion.py [--force]

This script is IDEMPOTENT — safe to run multiple times.
Use --force to force a re-ingest of all sources (replaces existing docs).

Rate limiting: 1.5s delay between fetches to be respectful to BIS servers.
"""

import os
import sys
import time
import logging
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

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_ingestion")

# ── Imports after env is loaded ───────────────────────────────────────────────
from app.database import SessionLocal
from app.ingestion.pipeline import ingest_source
from app.ingestion.sources import BIS_SOURCES
import app.models  # noqa: F401 — register all models

# Rate limit delay between source fetches (seconds)
FETCH_DELAY = 1.5


def main() -> None:
    force = "--force" in sys.argv

    logger.info("=" * 60)
    logger.info("BIS Sahayak — Chapter 14 Ingestion")
    logger.info("Sources to process: %d", len(BIS_SOURCES))
    logger.info("Force re-ingest:    %s", force)
    logger.info("=" * 60)

    db = SessionLocal()

    total_docs = 0
    total_chunks = 0
    skipped = 0
    failed: list[str] = []
    failed_details: list[str] = []

    try:
        for i, source in enumerate(BIS_SOURCES, start=1):
            logger.info("[%d/%d] Processing: %s", i, len(BIS_SOURCES), source.url)
            result = ingest_source(source, db, force_reingest=force)

            if result.skipped:
                logger.info("  [SKIP]  Already in DB")
                skipped += 1
            elif result.ok:
                logger.info("  [OK]    %d chunks", result.chunks_inserted)
                total_docs += 1
                total_chunks += result.chunks_inserted
            else:
                logger.error("  [FAIL]  %s", result.error)
                failed.append(source.url)
                failed_details.append(f"{source.url}: {result.error}")

            # Rate limit between fetches to be respectful to BIS servers
            if i < len(BIS_SOURCES):
                time.sleep(FETCH_DELAY)

    finally:
        db.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  CHAPTER 14 INGESTION COMPLETE")
    print()
    print(f"  Sources registered : {len(BIS_SOURCES)}")
    print(f"  Documents inserted : {total_docs}")
    print(f"  Chunks inserted    : {total_chunks}")
    print(f"  Sources skipped    : {skipped}  (already in DB)")
    print(f"  Sources failed     : {len(failed)}")
    if failed_details:
        print()
        print("  Failed sources:")
        for f in failed_details:
            print(f"    - {f}")
    print("=" * 60)

    if failed and total_docs == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
