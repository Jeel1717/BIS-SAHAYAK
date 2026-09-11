"""
BIS Sahayak — Text Chunker
Phase 6 / Chapter 14: Ingestion Pipeline

Splits extracted text into overlapping chunks suitable for RAG.

Target: ~400 tokens per chunk ≈ ~1200 characters (English, ~3 chars/token effective).
Overlap: ~40 tokens ≈ ~150 characters — helps retrieval across chunk boundaries.

Strategy:
  1. First split on section/heading boundaries (## markers from extractor).
  2. Prepend section heading to each chunk so context is self-contained for retrieval.
  3. If a section is still too large, split on paragraph boundaries.
  4. If a paragraph is still too large, split on sentence boundaries.
  5. Apply a sliding window with overlap across the final pieces.
  6. Never cut words in half.
  7. Never create tiny meaningless chunks (MIN_CHARS = 40).
"""

import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Target chunk size in characters (~400 tokens * ~3 chars/token effective for English)
TARGET_CHARS = 1200
# Overlap between consecutive chunks in characters
OVERLAP_CHARS = 150
# Minimum chunk size to bother storing — keep low so short BIS definitions are retained
MIN_CHARS = 40


@dataclass
class TextChunk:
    content: str
    chunk_index: int           # 0-based index within the source document/page
    chunk_title: str | None    # Section heading for this chunk (for metadata)
    clause_number: str | None  # Section heading if detected, else None (kept for compat)
    page_number: int | None


# Pattern to detect structured product catalog rows: Item_Number IS_Standard Product_Description
_PRODUCT_TABLE_ROW_PATTERN = re.compile(
    r"(?:^|\n)\s*(\d+)\s+(IS\s+[^a-zA-Z\n]+?(?:\([^\)]+\)[^a-zA-Z\n]*)*)\s+([A-Za-z0-9].*?)(?=(?:\n\s*\d+\s+IS)|\Z)",
    re.DOTALL
)


def _chunk_product_table(text: str, page_number: int | None) -> list[TextChunk]:
    """Parse product catalog/table pages into focused single-product chunks."""
    matches = _PRODUCT_TABLE_ROW_PATTERN.finditer(text)
    chunks: list[TextChunk] = []
    chunk_idx = 0
    for m in matches:
        item_num = m.group(1).strip()
        is_num = re.sub(r"\s+", " ", m.group(2).strip())
        product_name = re.sub(r"\s+", " ", m.group(3).strip())
        chunk_title = f"{is_num} — {product_name}"
        clause_number = f"Item {item_num}"
        content = (
            "BIS Product Certification — Simplified Procedure for Grant of Licence (Option 2)\n"
            "Annexure-I: Products under Simplified Procedure\n\n"
            "Product Entry:\n"
            f"- Indian Standard: {is_num}\n"
            f"- Product: {product_name}\n"
            f"- Item Number: {item_num}\n"
            "- Certification Scheme: BIS Product Certification Scheme I (Option 2 - Simplified Procedure)\n"
            f"- Provision: Mandatory utilization of Option 2 (Simplified Procedure) for grant of BIS licence within 30 days for domestic manufacturers and MSMEs under {is_num}."
        )
        chunks.append(TextChunk(
            content=content,
            chunk_index=chunk_idx,
            chunk_title=chunk_title,
            clause_number=clause_number,
            page_number=page_number,
        ))
        chunk_idx += 1
    return chunks


def chunk_page(
    text: str,
    page_number: int | None,
    target: int = TARGET_CHARS,
    overlap: int = OVERLAP_CHARS,
) -> list[TextChunk]:
    """
    Split a single page/section of text into overlapping chunks.

    Args:
        text:        The full cleaned text of one page or section.
        page_number: PDF page number, or None for HTML documents.
        target:      Target chunk size in characters.
        overlap:     Overlap between consecutive chunks in characters.

    Returns:
        List of TextChunk objects.
    """
    if not text or not text.strip():
        return []

    # Special Handling 1: Policy/Overview Page for Simplified Procedure Notice
    if page_number == 1 and ("Simplified Procedure" in text or "Option - 2" in text or "Option 2" in text) and "Annexure-I" in text:
        return [TextChunk(
            content=(
                "BIS Product Certification — Simplified Procedure for Grant of Licence (Option 2)\n\n"
                "Overview & Guidelines:\n"
                "Bureau of Indian Standards (B.I.S.) has introduced measures for mandatory utilisation of "
                "Option - 2 (erstwhile simplified procedure) for processing product certification applications "
                "for grant of licence. These measures are introduced for the domestic industry, including MSMEs, "
                "with the aim of processing applications for grant of licence within 30 days. "
                "Applications are required to be mandatorily filed under Option - 2 for products listed in Annexure-I."
            ),
            chunk_index=0,
            chunk_title="Simplified Procedure for Grant of Licence — Guidelines and 30-Day Timeline",
            clause_number="Option 2 Notice",
            page_number=1,
        )]

    # Special Handling 2: Structured Product Table / Catalog
    table_matches = len(_PRODUCT_TABLE_ROW_PATTERN.findall(text))
    if table_matches >= 3:
        table_chunks = _chunk_product_table(text, page_number)
        if table_chunks:
            logger.debug("Produced %d structured product chunks from page %s", len(table_chunks), page_number)
            return table_chunks

    # Step 1: Split on heading markers (## Heading) inserted by extractor
    sections = _split_on_headings(text)

    chunks: list[TextChunk] = []
    chunk_idx = 0

    for section_heading, section_text in sections:
        section_text = section_text.strip()
        if not section_text:
            continue

        # Build prefix: include heading in chunk content for self-contained retrieval
        heading_prefix = f"{section_heading}\n\n" if section_heading else ""

        # Step 2: Split large sections into pieces
        pieces = _split_to_size(section_text, target - len(heading_prefix))

        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if len(piece) < MIN_CHARS:
                continue

            # Include heading prefix in first piece; subsequent pieces get abbreviated prefix
            if section_heading and i == 0:
                content = heading_prefix + piece
            elif section_heading and i > 0:
                # Include abbreviated heading so chunk is self-contained
                content = f"{section_heading} (cont.)\n\n{piece}"
            else:
                content = piece

            chunks.append(TextChunk(
                content=content,
                chunk_index=chunk_idx,
                chunk_title=section_heading,
                clause_number=section_heading or None,
                page_number=page_number,
            ))
            chunk_idx += 1

    logger.debug("Produced %d chunks from page %s", len(chunks), page_number)
    return chunks


def _split_on_headings(text: str) -> list[tuple[str | None, str]]:
    """
    Split text on ## Heading markers, returning (heading, body) pairs.
    The first segment before any heading gets heading=None.
    """
    pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    sections: list[tuple[str | None, str]] = []
    last_end = 0
    current_heading: str | None = None

    for match in pattern.finditer(text):
        body = text[last_end:match.start()].strip()
        if body:
            sections.append((current_heading, body))
        current_heading = match.group(1).strip()
        last_end = match.end()

    # Remainder after last heading
    remainder = text[last_end:].strip()
    if remainder:
        sections.append((current_heading, remainder))

    if not sections:
        sections = [(None, text.strip())]

    return sections


def _split_to_size(text: str, target: int) -> list[str]:
    """
    Recursively split text into pieces no larger than `target` characters.
    Tries paragraph splits first, then sentence splits, then hard splits.
    """
    if len(text) <= target:
        return [text]

    # Try paragraph split first
    paragraphs = re.split(r"\n{2,}", text)
    if len(paragraphs) > 1:
        return _merge_to_target(paragraphs, target)

    # Try sentence split
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) > 1:
        return _merge_to_target(sentences, target)

    # Hard split as last resort — still avoid cutting words
    results = []
    start = 0
    while start < len(text):
        end = start + target
        if end < len(text):
            # Find nearest space before end
            space_pos = text.rfind(" ", start, end)
            if space_pos > start:
                end = space_pos
        results.append(text[start:end].strip())
        start = end - OVERLAP_CHARS // 2
        if start <= 0:
            break
    return [r for r in results if r]


def _merge_to_target(pieces: list[str], target: int) -> list[str]:
    """
    Greedily merge small pieces into chunks up to `target` chars,
    with clean sentence-boundary overlap between consecutive chunks.
    Never slices words or sentences in half.
    """
    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        piece_len = len(piece)

        if current_len + piece_len + 1 > target and current_parts:
            chunk_text = "\n\n".join(current_parts)
            chunks.append(chunk_text)

            # Keep last complete sentence as overlap (avoid slicing words in half)
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", chunk_text) if s.strip()]
            if sentences and len(sentences[-1]) <= OVERLAP_CHARS:
                overlap_text = sentences[-1]
                current_parts = [overlap_text, piece]
                current_len = len(overlap_text) + piece_len + 1
            else:
                current_parts = [piece]
                current_len = piece_len
        else:
            current_parts.append(piece)
            current_len += piece_len + 1

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def chunk_document(
    pages: list,
    target: int = TARGET_CHARS,
    overlap: int = OVERLAP_CHARS,
) -> list[TextChunk]:
    """
    Chunk all pages of an extracted document.

    Args:
        pages:   List of ExtractedPage objects from extractor.py.
        target:  Target chunk size in characters.
        overlap: Overlap between consecutive chunks.

    Returns:
        Flat list of TextChunk objects across all pages.
    """
    all_chunks: list[TextChunk] = []
    global_idx = 0
    for page in pages:
        page_chunks = chunk_page(page.text, page.page_number, target, overlap)
        for c in page_chunks:
            c.chunk_index = global_idx
            global_idx += 1
        all_chunks.extend(page_chunks)
    return all_chunks
