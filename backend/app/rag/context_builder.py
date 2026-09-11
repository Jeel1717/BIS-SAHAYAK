"""
BIS Sahayak — Context Builder
Phase 7 & Chapter 14: RAG / AI Brain

Formats retrieved BIS chunks into a grounded context string
suitable for passing to Gemini 3.7 Flash or other LLMs.

Design principles:
  1. Only include retrieved BIS chunks — no hallucinated content.
  2. Clearly label each source [1], [2], … with title and official URL.
  3. Include metadata (title, URL, clause) for traceability.
  4. System prompt enforces:
     - Answer ONLY from the provided sources.
     - Produce structured, readable markdown answers.
     - Cite every factual claim with [1], [2], etc.
     - Explain technical BIS terms in plain language.
     - Say that available BIS sources do not contain enough info when insufficient.
  5. Allow up to 5 unique sources per query for complex questions.
"""

from dataclasses import dataclass, field
from app.rag.retriever import RetrievalResult, RetrievedChunk

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are BIS Sahayak, an AI assistant for the Bureau of Indian Standards (BIS) of India.

CRITICAL RULES:
- Answer using ONLY the supplied BIS retrieved context below.
- Do NOT invent facts, standards, certification requirements, dates, fees, procedures, or legal claims.
- If the supplied context does not contain enough information to answer confidently, clearly say so.
- NEVER say "please visit the BIS website" as the primary answer — provide the explanation from the context first.
- Never claim a certification requirement or mandatory status unless the retrieved evidence explicitly supports it.
- Never infer that a product is covered by a standard simply because some BIS document was retrieved. If the retrieved evidence does not specifically mention or cover the user's requested product, explicitly state that available BIS sources do not contain sufficient evidence for that product.
- Preserve exact Indian Standard numbers (e.g. IS 2347), product names, clauses, and citation markers ([1], [2]).
- NEVER copy, dump, or repeat raw retrieved chunks, raw tables, or product lists verbatim. Always synthesize the facts into a natural, conversational, and well-structured response.
- Do not expose internal retrieval/debug information or raw database IDs.
- Cite every factual claim with the corresponding source citation marker [1], [2], etc.

ANSWER STYLE:
- Start with a direct answer in 1–2 sentences addressing the user's question immediately.
- Then use short bullet points when summarizing standards, requirements, or steps.
- Mention the applicable Indian Standard clearly (e.g., IS 2347 — Domestic Pressure Cookers).
- Mention the certification scheme/procedure only when supported by the retrieved evidence.
- Explain in simple language. Do not simply copy the entire retrieved chunk.
- Keep normal answers around 80–180 words unless the question genuinely requires more detail (40–100 words for simple questions).
- For broad questions, organize the answer with clean headings and bullets.
- End with a short practical next step or follow-up offer when appropriate.

The retrieved material comes from official BIS public sources."""

NO_INFORMATION_RESPONSE = (
    "I couldn't find enough information in the BIS knowledge base to answer this confidently. "
    "Try asking about BIS certification, hallmarking, HUID, Indian Standards, testing, laboratories, or consumer complaints."
)


@dataclass
class BuiltContext:
    """The formatted context ready to be sent to an LLM."""
    system_prompt: str
    sources_block: str          # The numbered [1]...[N] sources
    user_question: str
    has_information: bool
    source_chunks: list[RetrievedChunk] = field(default_factory=list)

    @property
    def full_prompt(self) -> str:
        """Combine system prompt + sources + question into one string."""
        if not self.has_information:
            return (
                f"{self.system_prompt}\n\n"
                f"SOURCES:\n(No relevant BIS information found)\n\n"
                f"USER QUESTION: {self.user_question}"
            )
        return (
            f"{self.system_prompt}\n\n"
            f"SOURCES:\n{self.sources_block}\n\n"
            f"USER QUESTION: {self.user_question}"
        )


def build_context(result: RetrievalResult) -> BuiltContext:
    """
    Convert a RetrievalResult into a BuiltContext for an LLM.

    Args:
        result: RetrievalResult from retriever.retrieve().

    Returns:
        BuiltContext with system prompt, numbered sources, and question.
    """
    if not result.found or not result.chunks:
        return BuiltContext(
            system_prompt=SYSTEM_PROMPT,
            sources_block="",
            user_question=result.query,
            has_information=False,
            source_chunks=[],
        )

    # Deduplicate sources by source_url (preferring highest similarity, max 3 unique sources)
    url_to_num: dict[str, int] = {}
    unique_chunks: list[RetrievedChunk] = []

    for chunk in result.chunks:
        url_norm = chunk.source_url.strip()
        if url_norm not in url_to_num:
            if len(url_to_num) >= 3:
                continue
            url_to_num[url_norm] = len(url_to_num) + 1
            unique_chunks.append(chunk)

    # Build source blocks — include all retrieved chunks (even from same URL)
    # so the LLM has full context, but citation numbers map to unique URLs
    source_lines: list[str] = []
    for chunk in result.chunks:
        url_norm = chunk.source_url.strip()
        num = url_to_num.get(url_norm)
        if num is None:
            continue
        meta_lines = [
            f"[{num}] {chunk.document_title}",
            f"Source: {chunk.source_url}",
        ]
        if chunk.clause_number:
            meta_lines.append(f"Section: {chunk.clause_number}")
        if chunk.page_number:
            meta_lines.append(f"Page: {chunk.page_number}")
        meta_lines.append(f"Content:\n{chunk.content}")
        source_lines.append("\n".join(meta_lines))

    sources_block = "\n\n---\n\n".join(source_lines)

    return BuiltContext(
        system_prompt=SYSTEM_PROMPT,
        sources_block=sources_block,
        user_question=result.query,
        has_information=True,
        source_chunks=unique_chunks,
    )


def format_citation_list(context: BuiltContext) -> str:
    """
    Format a readable citation list for displaying to the user after an answer.

    Example output:
        Sources:
        [1] BIS Consumer FAQ — https://www.bis.gov.in/...
        [2] BIS Hallmarking Guide — https://www.bis.gov.in/...
    """
    if not context.has_information:
        return ""

    lines = ["Sources:"]
    seen_urls: set[str] = set()

    for i, chunk in enumerate(context.source_chunks, start=1):
        url = chunk.source_url
        if url in seen_urls:
            continue
        seen_urls.add(url)
        lines.append(f"  [{i}] {chunk.document_title} — {url}")

    return "\n".join(lines)
