"""
BIS Sahayak — Ingestion Pipeline
Phase 6: BIS Knowledge Base

Orchestrates: Fetch → Extract → Chunk → Store (with duplicate prevention).

Usage:
    from app.ingestion.pipeline import ingest_source, SourceConfig

Each SourceConfig describes one BIS public URL to ingest.
The pipeline is idempotent: re-running it will not create duplicate documents
or chunks — it checks source_url before inserting.
"""

import logging
import uuid
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.ingestion.fetcher import fetch
from app.ingestion.extractor import extract
from app.ingestion.chunker import chunk_document
from app.models.document import Document, Chunk

logger = logging.getLogger(__name__)


@dataclass
class SourceConfig:
    """Describes one BIS public source to ingest."""
    url: str
    title: str                              # Human-readable title override
    document_type: str                      # e.g. "FAQ", "Consumer Guide", "About BIS"
    standard_number: str | None = None      # e.g. "IS 14543" — usually None for web pages
    version_or_effective_date: str | None = None


@dataclass
class IngestionResult:
    url: str
    title: str
    document_id: uuid.UUID | None = None
    chunks_inserted: int = 0
    skipped: bool = False        # True if document already existed
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def ingest_source(source: SourceConfig, db: Session, force_reingest: bool = False) -> IngestionResult:
    """
    Ingest a single BIS source URL into the database.

    Steps:
      1. Check if document already exists (by source_url) — skip if yes, or delete if force_reingest.
      2. Fetch the URL.
      3. Extract text.
      4. Chunk the text.
      5. Insert Document + Chunks in one transaction.

    Args:
        source: SourceConfig describing the URL to ingest.
        db:     Active SQLAlchemy Session.
        force_reingest: If True, replaces existing document and chunks.

    Returns:
        IngestionResult with outcome details.
    """
    logger.info("--- Ingesting: %s", source.url)

    # ── Step 1: Duplicate check ──────────────────────────────────────────────
    existing = db.query(Document).filter(Document.source_url == source.url).first()
    if existing:
        if force_reingest:
            logger.info("force_reingest=True: Replacing existing document %s for %s", existing.id, source.url)
            db.delete(existing)
            db.commit()
        else:
            logger.info("SKIP: Document already exists for %s (id=%s)", source.url, existing.id)
            return IngestionResult(
                url=source.url,
                title=source.title,
                document_id=existing.id,
                chunks_inserted=0,
                skipped=True,
            )

    # ── Step 2: Fetch ────────────────────────────────────────────────────────
    fetch_result = fetch(source.url)
    if not fetch_result.ok:
        logger.error("Fetch failed for %s: %s", source.url, fetch_result.error)
        return IngestionResult(
            url=source.url,
            title=source.title,
            error=f"Fetch failed: {fetch_result.error}",
        )

    # ── Step 3: Extract ──────────────────────────────────────────────────────
    extract_result = extract(fetch_result.content, fetch_result.kind, source.url)
    if not extract_result.ok:
        logger.error("Extract failed for %s: %s", source.url, extract_result.error)
        return IngestionResult(
            url=source.url,
            title=source.title,
            error=f"Extract failed: {extract_result.error}",
        )

    # Use extracted title only if we don't have a better override
    final_title = source.title or extract_result.title

    # ── Step 4: Chunk ────────────────────────────────────────────────────────
    text_chunks = chunk_document(extract_result.pages)
    if not text_chunks:
        logger.warning("No chunks produced for %s", source.url)
        return IngestionResult(
            url=source.url,
            title=final_title,
            error="No chunks produced — content may be too short or empty",
        )

    logger.info("Produced %d chunks for: %s", len(text_chunks), source.url)

    # ── Step 5: Insert Document + Chunks ─────────────────────────────────────
    try:
        doc_id = uuid.uuid4()
        document = Document(
            id=doc_id,
            title=final_title,
            standard_number=source.standard_number,
            source_url=source.url,
            document_type=source.document_type,
            version_or_effective_date=source.version_or_effective_date,
        )
        db.add(document)
        db.flush()  # write document to get its id (before chunks reference it)

        for tc in text_chunks:
            chunk = Chunk(
                id=uuid.uuid4(),
                document_id=doc_id,
                content=tc.content,
                chunk_title=getattr(tc, "chunk_title", None),
                clause_number=tc.clause_number,
                page_number=tc.page_number,
                embedding=None,  # embeddings added in generate_embeddings.py
            )
            db.add(chunk)

        db.commit()
        logger.info(
            "Inserted document %s with %d chunks", doc_id, len(text_chunks)
        )
        return IngestionResult(
            url=source.url,
            title=final_title,
            document_id=doc_id,
            chunks_inserted=len(text_chunks),
        )

    except Exception as e:
        db.rollback()
        logger.error("DB insert failed for %s: %s", source.url, e)
        return IngestionResult(
            url=source.url,
            title=final_title,
            error=f"DB insert failed: {type(e).__name__}: {e}",
        )
