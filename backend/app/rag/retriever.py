"""
BIS Sahayak — pgvector Retrieval Service with Domain Expansion & Hybrid Scoring
Phase 7 / Chapter 14 / Chapter 15: RAG / AI Brain

Performs semantic similarity search over embedded BIS chunks using pgvector,
combined with:
  1. Domain entity detection & targeted query expansion.
  2. Candidate retrieval (top semantic candidates + explicit keyword matches).
  3. Hybrid scoring (semantic similarity + standard number boost + lexical relevance +
     product specificity boost - generic administrative penalty).
  4. Preserves full chunk and document metadata (chunk_title, standard_number, clause_number).

Configuration (via .env):
  RETRIEVAL_TOP_K                 Number of results to return (default: 8)
  RETRIEVAL_SIMILARITY_THRESHOLD  Minimum similarity threshold (default: 0.185)
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.rag.embedder import embed_text
from app.rag.query_processor import (
    detect_domain_entities,
    expand_query_for_embedding,
    extract_primary_keyword,
    calculate_hybrid_score,
)

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 8
DEFAULT_THRESHOLD = 0.185             # Calibrated cosine similarity threshold for general chat
DEFAULT_ASSESSMENT_THRESHOLD = 0.50   # Strict relevance threshold for structured product assessment


@dataclass
class RetrievedChunk:
    """A single chunk returned by similarity search."""
    chunk_id: str
    document_id: str
    document_title: str
    document_type: str | None
    source_url: str
    content: str
    clause_number: str | None
    page_number: int | None
    similarity: float   # 0.0 – 1.0; higher = more similar
    chunk_title: str | None = None
    standard_number: str | None = None


@dataclass
class RetrievalResult:
    query: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    below_threshold: bool = False  # True when best match is below the threshold

    @property
    def found(self) -> bool:
        return bool(self.chunks) and not self.below_threshold


def _execute_search(
    query_vector: list[float],
    db: Session,
    candidate_k: int,
    distance_threshold: float,
    keyword_pattern: str | None = None,
) -> list:
    """Execute hybrid candidate search returning semantic + keyword matches."""
    has_kw = keyword_pattern is not None
    kw = keyword_pattern or ""

    sql = text("""
        WITH semantic_matches AS (
            SELECT
                c.id          AS chunk_id,
                c.document_id,
                c.content,
                c.chunk_title,
                c.clause_number,
                c.page_number,
                d.title       AS document_title,
                d.standard_number,
                d.document_type,
                d.source_url,
                1 - (c.embedding <=> CAST(:query_vec AS vector)) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
              AND (c.embedding <=> CAST(:query_vec AS vector)) <= :dist_thresh
            ORDER BY c.embedding <=> CAST(:query_vec AS vector)
            LIMIT :candidate_k
        ),
        keyword_matches AS (
            SELECT
                c.id          AS chunk_id,
                c.document_id,
                c.content,
                c.chunk_title,
                c.clause_number,
                c.page_number,
                d.title       AS document_title,
                d.standard_number,
                d.document_type,
                d.source_url,
                1 - (c.embedding <=> CAST(:query_vec AS vector)) AS similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
              AND :has_kw = true
              AND (c.content ILIKE :kw OR d.title ILIKE :kw)
            LIMIT 20
        )
        SELECT * FROM semantic_matches
        UNION
        SELECT * FROM keyword_matches
    """)

    vec_literal = "[" + ",".join(f"{v:.8f}" for v in query_vector) + "]"

    return db.execute(sql, {
        "query_vec": vec_literal,
        "dist_thresh": distance_threshold,
        "candidate_k": candidate_k,
        "has_kw": has_kw,
        "kw": kw,
    }).fetchall()


def extract_target_product_from_query(query: str) -> str | None:
    """
    Extract primary product or item name from an assessment prompt or product question.
    Examples:
      'Analyze this product for BIS requirements... Product: helmet ...' -> 'helmet'
      'What are the BIS requirements for helmets?' -> 'helmets'
      'What BIS requirements apply to pressure cookers?' -> 'pressure cookers'
    """
    import re

    # 1. Check for explicit 'Product: <name>' in assessment prompt
    m = re.search(r"Product:\s*([^\n\r]+)", query, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        if val:
            return val

    # 2. Check for question patterns like 'requirements (apply) to/for <product>'
    p_m = re.search(
        r"(?:requirements(?:\s+apply)?\s+(?:to|for)|standard\s+(?:for|applies\s+to)|certification\s+for)\s+([^\n\r?.,]+)",
        query,
        re.IGNORECASE,
    )
    if p_m:
        val = p_m.group(1).strip()
        if val:
            return val

    return None


def is_chunk_relevant_to_target_product(
    target_prod: str,
    content: str,
    doc_title: str,
    chunk_title: str | None = None,
    std_number: str | None = None,
) -> bool:
    """
    General, domain-agnostic relevance check:
    Verifies that the retrieved chunk actually mentions or addresses the product
    or standard specified by the user, rather than an unrelated document.
    """
    import re

    stopwords = {
        "the", "a", "an", "for", "in", "of", "and", "or", "to", "this", "that", "with",
        "product", "products", "requirements", "requirement", "bis", "indian", "standard",
        "standards", "is", "are", "does", "do", "what", "how", "can", "apply", "applicable",
        "certification", "procedure", "option", "scheme", "under", "about", "tell", "me",
        "item", "items", "entry", "entries", "list", "listed", "guidelines", "guide"
    }
    tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9]+\b", target_prod)]
    substantive = [t for t in tokens if t not in stopwords and len(t) >= 3]
    if not substantive:
        return True

    combined = f"{content} {doc_title} {chunk_title or ''} {std_number or ''}".lower()

    # Exact phrase match or token stem match
    phrase = " ".join(substantive)
    if phrase in combined:
        return True

    # Multi-word product: check if key distinctive term matches (e.g. 'cooker' in 'domestic pressure cooker')
    for term in substantive:
        # Check whole word or root match
        term_root = term.rstrip("s")
        if re.search(r"\b" + re.escape(term_root) + r"[s]?\b", combined):
            return True

    return False


def retrieve(
    query: str,
    db: Session,
    top_k: int | None = None,
    threshold: float | None = None,
) -> RetrievalResult:
    """
    Hybrid search: domain expansion + semantic candidate retrieval + lexical boosting.

    Args:
        query:     Natural-language question from the user.
        db:        Active SQLAlchemy Session.
        top_k:     Number of results (overrides env; default 8).
        threshold: Minimum cosine similarity (overrides env; default 0.185).

    Returns:
        RetrievalResult with matching chunks sorted by relevance (desc).
        Returns empty result with below_threshold=True when no match is good enough.
    """
    # 1. Detect target product constraint if present
    target_product = extract_target_product_from_query(query)
    is_assessment = bool(
        target_product and ("analyze this product" in query.lower() or "product:" in query.lower())
    )

    k = top_k if top_k is not None else int(os.environ.get("RETRIEVAL_TOP_K", DEFAULT_TOP_K))
    if threshold is not None:
        thresh = threshold
    elif is_assessment:
        thresh = float(os.environ.get("RETRIEVAL_ASSESSMENT_THRESHOLD", DEFAULT_ASSESSMENT_THRESHOLD))
    else:
        thresh = float(os.environ.get("RETRIEVAL_SIMILARITY_THRESHOLD", DEFAULT_THRESHOLD))

    logger.info("Retrieval query: %r (top_k=%d, threshold=%.2f, is_assessment=%s)", query[:80], k, thresh, is_assessment)

    # For structured assessment prompts, focus semantic search on the target product
    search_text = target_product if is_assessment else query

    # 2. Detect domain entities and expand query for embedding
    matched_entities = detect_domain_entities(search_text)
    expanded_query = expand_query_for_embedding(search_text, matched_entities)
    primary_kw = extract_primary_keyword(matched_entities)

    # 3. Embed the expanded query
    query_vector = embed_text(expanded_query)

    # 4. Search pgvector candidates
    distance_threshold = 1.0 - thresh
    candidate_k = max(k * 4, 30)
    rows = _execute_search(query_vector, db, candidate_k, distance_threshold, primary_kw)

    if not rows:
        logger.info("No results above threshold for query: %r", query[:80])
        return RetrievalResult(query=query, chunks=[], below_threshold=True)

    # 4. Hybrid scoring & reranking
    scored_candidates = []
    for row in rows:
        raw_sim = float(row.similarity)
        final_score = calculate_hybrid_score(
            raw_similarity=raw_sim,
            content=row.content,
            doc_title=row.document_title,
            chunk_title=row.chunk_title,
            standard_number=row.standard_number,
            query=query,
            matched_entities=matched_entities,
        )

        # Only retain chunks meeting the threshold
        if final_score >= thresh:
            # Normalize/clamp similarity to strictly valid [0.0, 1.0] range
            if final_score >= 1.0:
                bounded_sim = min(0.9999, 0.90 + 0.09 * (final_score / (final_score + 1.0)))
            else:
                bounded_sim = max(0.0001, min(0.9999, final_score))

            chunk_std = row.standard_number
            if not chunk_std and row.chunk_title:
                import re as _re
                m = _re.match(r"^(IS\s+[^—\n]+)", row.chunk_title)
                if m:
                    chunk_std = m.group(1).strip()

            chunk = RetrievedChunk(
                chunk_id=str(row.chunk_id),
                document_id=str(row.document_id),
                document_title=row.document_title,
                document_type=row.document_type,
                source_url=row.source_url,
                content=row.content,
                clause_number=row.clause_number,
                page_number=row.page_number,
                similarity=bounded_sim,
                chunk_title=row.chunk_title,
                standard_number=chunk_std,
            )
            scored_candidates.append((final_score, chunk))

    # Strict Relevance Gate: When a specific product is targeted, verify
    # that the candidate chunk actually mentions or relates to that product.
    if target_product:
        scored_candidates = [
            (score, chunk)
            for score, chunk in scored_candidates
            if is_chunk_relevant_to_target_product(
                target_product,
                chunk.content,
                chunk.document_title,
                chunk.chunk_title,
                chunk.standard_number,
            )
        ]

    if not scored_candidates:
        logger.info("No candidates above threshold or relevant to %r for query: %r", target_product, query[:80])
        return RetrievalResult(query=query, chunks=[], below_threshold=True)

    # 5. Sort by final score descending and select top-k
    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    best_raw_score = scored_candidates[0][0]

    # For product-specific queries with strong focused matches, drop heavily penalized
    # multi-standard catalog chunks that are far below the top match
    if best_raw_score > 1.2 and matched_entities and any(e.is_product for e in matched_entities):
        cutoff = best_raw_score * 0.50
        scored_candidates = [item for item in scored_candidates if item[0] >= cutoff]

    top_chunks = [chunk for _, chunk in scored_candidates[:k]]

    logger.info(
        "Retrieved %d chunks, best score=%.3f, bounded_sim=%.3f",
        len(top_chunks), scored_candidates[0][0], top_chunks[0].similarity
    )
    return RetrievalResult(query=query, chunks=top_chunks, below_threshold=False)

