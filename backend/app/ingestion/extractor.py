"""
BIS Sahayak — Text Extractor
Phase 6 / Chapter 14: Ingestion Pipeline

Extracts clean, meaningful text from:
  - HTML pages  (via BeautifulSoup + lxml)
  - PDF bytes   (via pypdf)

Strategy for HTML:
  1. Parse with lxml (fast).
  2. Remove script, style, nav, footer, sidebar, form elements.
  3. Try to find the main content container first — multiple BIS-specific patterns.
  4. Walk remaining elements preserving heading hierarchy as ## markers.
  5. Preserve numbered steps, bullet lists, definitions, tables.
  6. Collapse excess whitespace and blank lines.
  7. Deduplicate repeated lines (nav/chrome residue).

Strategy for PDF:
  1. Parse with pypdf.
  2. Extract text page by page.
  3. Track page numbers for chunk metadata.
  4. Clean obvious PDF extraction artefacts.
"""

import io
import logging
import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

# Tags whose content we always discard
_NOISE_TAGS = {
    "script", "style", "noscript", "nav", "footer",
    "form", "button", "iframe", "svg", "img", "figure",
    "select", "option", "input", "textarea", "meta", "link",
}

# CSS class/id fragments indicating navigation or chrome — kept specific to avoid false positives
_NOISE_PATTERNS = re.compile(
    r"(^nav$|^menu$|^header$|^footer$|^sidebar$|breadcrumb|cookie|"
    r"^social$|^share$|^search$|advertisement|popup|modal|"
    r"carousel|slider|skip-to|back-to-top|top-bar|lang-switcher)",
    re.IGNORECASE,
)

# BIS-specific main content container CSS class patterns (in order of preference)
_BIS_CONTENT_CLASSES = [
    "who_we_area",       # Main BIS content wrapper
    "entry-content",     # WordPress content
    "page-content",
    "main-content",
    "content-area",
    "post-content",
    "single-content",
]


@dataclass
class ExtractedPage:
    """Text extracted from one logical page / section."""
    text: str
    page_number: int | None = None  # only for PDFs


@dataclass
class ExtractResult:
    title: str
    pages: list[ExtractedPage] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.pages)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.text for p in self.pages)


# ── HTML extraction ───────────────────────────────────────────────────────────

def _safe_tag_attrs(tag: Tag) -> tuple[str, str]:
    """
    Safely extract class and id strings from a Tag.
    BS4 4.13 can produce Tag objects with name=None or attrs=None.
    """
    if not isinstance(tag, Tag) or tag.name is None or tag.attrs is None:
        return "", ""
    cls = " ".join(tag.attrs.get("class", []) or [])
    tid = tag.attrs.get("id", "") or ""
    return cls, tid


def _is_noise(tag) -> bool:
    """Return True if this tag is likely navigation/chrome noise."""
    if not isinstance(tag, Tag) or tag.name is None:
        return False
    if tag.name in _NOISE_TAGS:
        return True
    cls, tid = _safe_tag_attrs(tag)
    return bool(_NOISE_PATTERNS.search(cls) or _NOISE_PATTERNS.search(tid))


def _find_content_root(soup: BeautifulSoup):
    """Find the primary content container on a BIS portal page."""
    # Try BIS-specific class patterns
    for cls_pattern in _BIS_CONTENT_CLASSES:
        found = soup.find("div", class_=lambda c: c and cls_pattern in c)
        if found:
            return found

    # Try id-based skip-to-content links
    for id_pattern in ["skip-to-main-content", "main-content", "content", "main"]:
        found = soup.find(attrs={"id": id_pattern})
        if found:
            return found

    # Standard semantic elements
    for tag in ["main", "article"]:
        found = soup.find(tag)
        if found:
            return found

    return soup.body or soup


def extract_html(html_bytes: bytes, source_url: str) -> ExtractResult:
    """
    Extract clean, meaningful text from an official BIS HTML page.
    Targets the main content container and filters out sidebars,
    navigation chrome, and amendment history tables.
    """
    try:
        soup = BeautifulSoup(html_bytes, "lxml")

        # Title — prefer og:title or <title>
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            raw_title = og_title["content"].strip()
        else:
            title_tag = soup.find("title")
            raw_title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        title = re.sub(
            r"\s*[-|]\s*Bureau of Indian Standards.*$", "", raw_title, flags=re.IGNORECASE
        ).strip()
        if not title:
            title = raw_title

        # Locate the primary content container
        content_root = _find_content_root(soup)

        # Decompose known noise inside the content root
        for noise_tag in content_root.find_all([
            "script", "style", "nav", "footer", "form", "select", "iframe", "svg"
        ]):
            noise_tag.decompose()

        for noise_el in content_root.find_all(
            class_=re.compile(r"breadcrumb|sidebar|widget|menu|nav|amendment|cookie|social", re.I)
        ):
            noise_el.decompose()

        lines: list[str] = []
        seen_lines: set[str] = set()

        for el in content_root.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "dt", "dd", "blockquote"]
        ):
            text = el.get_text(separator=" ", strip=True)
            if not text or len(text) < 8:
                continue

            # Filter out navigation breadcrumbs
            if text.startswith("Home /") or "Breadcrumbs" in text:
                continue

            # Filter out repeated amendment history entries
            if re.search(
                r"Amendment\s+\d+\s+(?:January|February|March|April|May|June|July|"
                r"August|September|October|November|December)",
                text, re.I,
            ):
                continue

            cleaned_line = re.sub(r"\s+", " ", text).strip()
            if len(cleaned_line) < 8:
                continue

            # Deduplicate
            if cleaned_line in seen_lines:
                continue
            seen_lines.add(cleaned_line)

            if el.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                lines.append(f"\n## {cleaned_line}\n")
            elif el.name == "li":
                lines.append(f"- {cleaned_line}")
            elif el.name in ("dt",):
                lines.append(f"**{cleaned_line}**")
            elif el.name in ("dd",):
                lines.append(f"  {cleaned_line}")
            else:
                lines.append(cleaned_line)

        cleaned = "\n\n".join(lines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

        if len(cleaned) < 80:
            return ExtractResult(
                title=title,
                error=f"Extracted text too short ({len(cleaned)} chars) — page may be JS-rendered",
            )

        logger.info("Extracted %d clean chars from HTML: %s", len(cleaned), source_url)
        return ExtractResult(
            title=title,
            pages=[ExtractedPage(text=cleaned, page_number=None)],
        )

    except Exception as e:
        logger.error("HTML extraction failed for %s: %s", source_url, e)
        return ExtractResult(title="Unknown", error=str(e))


# ── PDF extraction ────────────────────────────────────────────────────────────

def extract_pdf(pdf_bytes: bytes, source_url: str) -> ExtractResult:
    """
    Extract text from a PDF, one page at a time.

    Returns an ExtractResult with one ExtractedPage per PDF page.
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))

        title = "Untitled PDF"
        if reader.metadata and reader.metadata.title:
            title = reader.metadata.title.strip()

        pages: list[ExtractedPage] = []
        for page_num, page in enumerate(reader.pages, start=1):
            raw = page.extract_text() or ""
            if not raw.strip():
                continue

            cleaned = _clean_pdf_text(raw)
            if len(cleaned) > 40:
                pages.append(ExtractedPage(text=cleaned, page_number=page_num))

        if not pages:
            return ExtractResult(title=title, error="No readable text found in PDF")

        logger.info("Extracted %d pages from PDF: %s", len(pages), source_url)
        return ExtractResult(title=title, pages=pages)

    except Exception as e:
        logger.error("PDF extraction failed for %s: %s", source_url, e)
        return ExtractResult(title="Unknown PDF", error=str(e))


def _clean_pdf_text(text: str) -> str:
    """Fix common PDF text extraction issues."""
    # Rejoin hyphenated line-breaks
    text = re.sub(r"-\n(\w)", r"\1", text)
    # Join mid-sentence line breaks
    text = re.sub(r"(?<!\n)\n(?!\n)(?=[a-z])", " ", text)
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── Dispatcher ────────────────────────────────────────────────────────────────

def extract(content: bytes, kind: str, source_url: str) -> ExtractResult:
    """Route to the correct extractor based on content kind."""
    if kind == "pdf":
        return extract_pdf(content, source_url)
    return extract_html(content, source_url)
