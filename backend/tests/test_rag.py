"""
BIS Sahayak — RAG Tests
Phase 7: RAG / AI Brain

Tests:
  1. Embedding generation and dimension validation
  2. Batch embedding consistency
  3. Context builder formatting
  4. Context builder with no results (threshold behavior)
  5. LLM interface stub behavior
  6. Retrieval (requires DB with embeddings — skipped if not available)

Usage:
    cd bis-sahayak/backend
    venv\\Scripts\\activate
    python -m pytest tests/ -v
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ── Load .env for test environment ────────────────────────────────────────────
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for _l in _env.read_text("utf-8").splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("="); os.environ.setdefault(k.strip(), v.strip())


# ── 1. Embedding generation ────────────────────────────────────────────────────

class TestEmbedder:
    """Tests for the local sentence-transformers embedder."""

    def test_embed_text_returns_list(self):
        from app.rag.embedder import embed_text
        vec = embed_text("What is the ISI mark?")
        assert isinstance(vec, list), "embed_text should return a list"
        assert len(vec) > 0, "embedding should not be empty"

    def test_embed_text_dimension(self):
        from app.rag.embedder import embed_text, get_embedding_dimension
        vec = embed_text("Bureau of Indian Standards")
        expected_dim = get_embedding_dimension()
        assert len(vec) == expected_dim, (
            f"Expected {expected_dim} dims, got {len(vec)}"
        )

    def test_embedding_dimension_is_384(self):
        """all-MiniLM-L6-v2 always produces 384-dim vectors."""
        from app.rag.embedder import get_embedding_dimension
        dim = get_embedding_dimension()
        assert dim == 384, f"Expected 384 dims for all-MiniLM-L6-v2, got {dim}"

    def test_embed_batch_length(self):
        from app.rag.embedder import embed_batch
        texts = ["ISI mark", "hallmarking", "BIS certification", "IS 14543"]
        vecs = embed_batch(texts)
        assert len(vecs) == len(texts), "batch output length must match input length"

    def test_embed_batch_consistent_with_single(self):
        """Batch embedding of one text should match single embedding."""
        from app.rag.embedder import embed_text, embed_batch
        text = "What is mandatory BIS certification?"
        single = embed_text(text)
        batch = embed_batch([text])
        assert len(batch) == 1
        # Values should be very close (floating point)
        for a, b in zip(single, batch[0]):
            assert abs(a - b) < 1e-5, "single and batch embeddings differ"

    def test_similar_texts_are_closer(self):
        """Semantically similar texts should produce closer vectors."""
        import math
        from app.rag.embedder import embed_text

        v1 = embed_text("hallmarked gold jewellery consumer rights")
        v2 = embed_text("gold hallmark BIS consumer protection")
        v3 = embed_text("income tax return filing procedure")

        def cosine(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = math.sqrt(sum(x * x for x in a))
            mag_b = math.sqrt(sum(x * x for x in b))
            return dot / (mag_a * mag_b)

        sim_related = cosine(v1, v2)
        sim_unrelated = cosine(v1, v3)
        assert sim_related > sim_unrelated, (
            f"Related texts ({sim_related:.3f}) should be more similar "
            f"than unrelated ({sim_unrelated:.3f})"
        )

    def test_normalized_embeddings(self):
        """Embeddings should be unit-normalized (L2 norm ≈ 1.0)."""
        import math
        from app.rag.embedder import embed_text
        vec = embed_text("BIS hallmarking")
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 1e-4, f"Expected unit norm, got {norm:.6f}"


# ── 2. Context Builder ─────────────────────────────────────────────────────────

class TestContextBuilder:
    """Tests for the RAG context builder."""

    def _make_chunk(self, i=1, similarity=0.75):
        from app.rag.retriever import RetrievedChunk
        return RetrievedChunk(
            chunk_id=f"chunk-{i}",
            document_id=f"doc-{i}",
            document_title=f"BIS Test Document {i}",
            document_type="FAQ",
            source_url=f"https://www.bis.gov.in/test/{i}/",
            content=f"This is test BIS content number {i} about hallmarking and consumer rights.",
            clause_number=f"Section {i}.1",
            page_number=i,
            similarity=similarity,
        )

    def _make_result(self, n_chunks=2, found=True):
        from app.rag.retriever import RetrievalResult
        chunks = [self._make_chunk(i, 0.75 - i * 0.05) for i in range(1, n_chunks + 1)]
        return RetrievalResult(
            query="What is BIS hallmarking?",
            chunks=chunks if found else [],
            below_threshold=not found,
        )

    def test_build_context_with_results(self):
        from app.rag.context_builder import build_context
        result = self._make_result(n_chunks=2)
        ctx = build_context(result)
        assert ctx.has_information is True
        assert "[1]" in ctx.sources_block
        assert "[2]" in ctx.sources_block
        assert "bis.gov.in" in ctx.sources_block

    def test_build_context_no_results(self):
        from app.rag.context_builder import build_context
        result = self._make_result(found=False)
        ctx = build_context(result)
        assert ctx.has_information is False
        assert ctx.sources_block == ""

    def test_full_prompt_contains_system_instructions(self):
        from app.rag.context_builder import build_context, SYSTEM_PROMPT
        result = self._make_result(n_chunks=1)
        ctx = build_context(result)
        prompt = ctx.full_prompt
        assert "BIS Sahayak" in prompt
        assert "CRITICAL RULES" in prompt
        assert "citation" in prompt.lower() or "[1]" in prompt or "Cite" in prompt

    def test_full_prompt_no_info_mentions_contact(self):
        from app.rag.context_builder import build_context
        result = self._make_result(found=False)
        ctx = build_context(result)
        prompt = ctx.full_prompt
        assert "No relevant BIS information found" in prompt

    def test_citation_list_format(self):
        from app.rag.context_builder import build_context, format_citation_list
        result = self._make_result(n_chunks=2)
        ctx = build_context(result)
        citations = format_citation_list(ctx)
        assert "Sources:" in citations
        assert "[1]" in citations

    def test_citation_list_empty_when_no_info(self):
        from app.rag.context_builder import build_context, format_citation_list
        result = self._make_result(found=False)
        ctx = build_context(result)
        citations = format_citation_list(ctx)
        assert citations == ""


# ── 3. LLM Interface ──────────────────────────────────────────────────────────

class TestLLMInterface:
    """Tests for the abstract LLM interface and StubLLM."""

    def _make_context(self, has_info=True):
        from app.rag.context_builder import BuiltContext
        from app.rag.retriever import RetrievedChunk
        chunks = []
        if has_info:
            chunks = [RetrievedChunk(
                chunk_id="c1", document_id="d1",
                document_title="BIS FAQ", document_type="FAQ",
                source_url="https://www.bis.gov.in/faq/",
                content="ISI mark certifies product quality.",
                clause_number=None, page_number=None, similarity=0.8
            )]
        return BuiltContext(
            system_prompt="Test prompt",
            sources_block="[1] Test source",
            user_question="What is ISI mark?",
            has_information=has_info,
            source_chunks=chunks,
        )

    def test_get_stub_llm(self):
        from app.rag.llm_interface import get_llm, StubLLM
        llm = get_llm("stub")
        assert isinstance(llm, StubLLM)

    def test_stub_llm_with_info(self):
        from app.rag.llm_interface import get_llm
        llm = get_llm("stub")
        ctx = self._make_context(has_info=True)
        response = llm.complete(ctx)
        assert isinstance(response, str)
        assert "STUB LLM" not in response
        assert "similarity=" not in response
        assert "[1]" in response

    def test_stub_llm_no_info(self):
        from app.rag.llm_interface import get_llm, NO_INFORMATION_RESPONSE
        from app.rag.context_builder import NO_INFORMATION_RESPONSE as ctx_msg
        llm = get_llm("stub")
        ctx = self._make_context(has_info=False)
        response = llm.complete(ctx)
        assert "enough" in response.lower() or "couldn't find" in response.lower() or "don't have" in response.lower()

    def test_unknown_provider_raises(self):
        from app.rag.llm_interface import get_llm
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm("paid_api_that_costs_money")


# ── 4. Retrieval (integration — requires embedded DB) ─────────────────────────

class TestRetrieval:
    """
    Integration tests for pgvector retrieval.
    These require the database to have embeddings — skip gracefully if not.
    """

    @pytest.fixture
    def db(self):
        from app.database import SessionLocal
        session = SessionLocal()
        yield session
        session.close()

    def _has_embeddings(self, db) -> bool:
        from sqlalchemy import text
        count = db.execute(text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")).scalar()
        return (count or 0) > 0

    def test_hallmarking_query_retrieves_results(self, db):
        if not self._has_embeddings(db):
            pytest.skip("No embeddings in DB yet — run generate_embeddings.py first")
        from app.rag.retriever import retrieve
        result = retrieve("What should a consumer check when buying hallmarked gold?", db, top_k=5)
        assert result.found, "Expected results for hallmarking query"
        assert len(result.chunks) > 0
        # At least one result should mention hallmarking
        all_content = " ".join(c.content.lower() for c in result.chunks)
        assert any(w in all_content for w in ["hallmark", "gold", "bis", "consumer", "purity"])

    def test_unrelated_query_below_threshold(self, db):
        if not self._has_embeddings(db):
            pytest.skip("No embeddings in DB yet — run generate_embeddings.py first")
        from app.rag.retriever import retrieve
        # This query has nothing to do with BIS standards
        result = retrieve(
            "Recipe for chocolate cake with fondant icing",
            db,
            top_k=5,
            threshold=0.60,  # strict threshold
        )
        assert not result.found, (
            "A cooking query should not exceed 0.60 similarity with BIS content"
        )
        assert result.below_threshold is True

    def test_retrieval_returns_source_metadata(self, db):
        if not self._has_embeddings(db):
            pytest.skip("No embeddings in DB yet — run generate_embeddings.py first")
        from app.rag.retriever import retrieve
        result = retrieve("BIS certification product", db, top_k=3)
        if not result.found:
            pytest.skip("No results above threshold for this query")
        for chunk in result.chunks:
            assert chunk.source_url.startswith("https://www.bis.gov.in")
            assert chunk.document_title
            assert 0.0 <= chunk.similarity <= 1.0

    def test_similarity_scores_in_range(self, db):
        if not self._has_embeddings(db):
            pytest.skip("No embeddings in DB yet — run generate_embeddings.py first")
        from app.rag.retriever import retrieve
        result = retrieve("Indian Standards BIS consumer", db, top_k=5, threshold=0.0)
        for chunk in result.chunks:
            assert 0.0 <= chunk.similarity <= 1.0, (
                f"Similarity {chunk.similarity} is out of [0, 1] range"
            )
