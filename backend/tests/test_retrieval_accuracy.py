"""
BIS Sahayak — Regression Tests for Natural-Language Retrieval Accuracy
Chapter 15: Verification of Domain Expansion & Product-Aware RAG Retrieval

Tests:
  A. "cooker" -> pressure-cooker-specific source appears in top results.
  B. "pressure cooker" -> IS 2347 / pressure cooker source appears prominently.
  C. "cooker certification" -> pressure cooker certification/Product Certification evidence.
  D. "what BIS standard applies to pressure cooker" -> IS 2347-related evidence.
  E. "does pressure cooker need BIS certification" -> relevant certification + pressure cooker evidence.
  F. "what is HUID" -> hallmarking/HUID sources, NOT pressure cooker.
  G. "how do I verify hallmarked gold" -> hallmarking/HUID sources.
  H. "how can a manufacturer obtain BIS certification" -> Product Certification Scheme I / certification sources.
  I. "how do I bake a chocolate cake" -> 0 BIS evidence and safe fallback.
"""

import pytest
from app.database import SessionLocal
from app.rag.retriever import retrieve


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def _has_embeddings(db) -> bool:
    from sqlalchemy import text
    count = db.execute(text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")).scalar()
    return (count or 0) > 0


class TestCookerNaturalLanguageRetrieval:
    """Test suite for pressure cooker natural-language query variations."""

    def test_query_cooker_retrieves_focused_is2347_source(self, db):
        """A. 'cooker' -> retrieves a focused chunk containing 'IS 2347' and 'Domestic Pressure Cookers'."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("cooker", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        top = res.chunks[0]
        assert "IS 2347" in top.content, "Expected IS 2347 in top retrieved cooker chunk"
        assert "Domestic Pressure Cookers" in top.content, "Expected Domestic Pressure Cookers in top cooker chunk"
        assert len(top.content) < 1000, f"Expected focused chunk (<1000 chars), got {len(top.content)}"

    def test_query_pressure_cooker_retrieves_focused_is2347(self, db):
        """B. 'pressure cooker' -> retrieves a focused chunk containing 'IS 2347' and 'Domestic Pressure Cookers'."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("pressure cooker", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        top = res.chunks[0]
        assert "IS 2347" in top.content
        assert "Domestic Pressure Cookers" in top.content
        assert len(top.content) < 1000

    def test_query_what_bis_requirements_apply_to_pressure_cookers(self, db):
        """C. 'What BIS requirements apply to pressure cookers?' -> focused pressure cooker evidence rather than giant list."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("What BIS requirements apply to pressure cookers?", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        top = res.chunks[0]
        assert "IS 2347" in top.content
        assert "Domestic Pressure Cookers" in top.content
        assert "Option 2" in top.content or "Simplified Procedure" in top.content

    def test_cooker_retrieval_does_not_contain_unrelated_products_list(self, db):
        """D. The retrieved context for cooker does NOT contain dozens/hundreds of unrelated product entries."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("cooker", db, top_k=3)
        assert res.found is True
        top = res.chunks[0]
        # Verify that unrelated standards that were adjacent in the raw PDF table do NOT appear in the focused chunk
        unrelated_standards = ["IS 12751", "IS 13983", "IS 14510", "IS 2567", "IS 2925"]
        for std in unrelated_standards:
            assert std not in top.content, f"Unrelated standard {std} should not be in focused cooker chunk"

    def test_query_is2347_retrieves_focused_chunk(self, db):
        """E. 'IS 2347' -> retrieves the focused IS 2347 chunk."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("IS 2347", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        top = res.chunks[0]
        assert "IS 2347" in top.content
        assert "Domestic Pressure Cookers" in top.content


class TestDomainEntityIsolationAndFallback:
    """Test suite ensuring non-cooker domain queries and out-of-scope queries remain accurate."""

    def test_query_what_is_huid_retrieves_hallmarking_not_cooker(self, db):
        """F. 'what is HUID' -> hallmarking/HUID sources, NOT pressure cooker."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("what is HUID", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        for c in res.chunks:
            assert "cooker" not in c.content.lower(), "Pressure cooker chunk leaked into HUID query!"
        doc_titles = " ".join(c.document_title.lower() for c in res.chunks)
        assert "hallmark" in doc_titles or "jewell" in doc_titles or "complaint" in doc_titles or "assay" in doc_titles

    def test_query_verify_hallmarked_gold_retrieves_hallmarking(self, db):
        """G. 'how do I verify hallmarked gold' -> hallmarking/HUID sources."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("how do I verify hallmarked gold", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        content_text = " ".join(c.content.lower() for c in res.chunks)
        assert "hallmark" in content_text or "jewell" in content_text or "gold" in content_text
        for c in res.chunks:
            assert "cooker" not in c.content.lower()

    def test_query_manufacturer_certification_retrieves_scheme_i(self, db):
        """H. 'how can a manufacturer obtain BIS certification' -> Scheme I / certification sources."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("how can a manufacturer obtain BIS certification", db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        doc_titles = " ".join(c.document_title.lower() for c in res.chunks)
        assert "certification" in doc_titles or "scheme" in doc_titles or "bis act" in doc_titles
        for c in res.chunks:
            assert "cooker" not in c.content.lower()

    def test_query_bake_chocolate_cake_returns_safe_fallback(self, db):
        """I. 'how do I bake a chocolate cake' -> 0 BIS evidence and safe fallback."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")
        res = retrieve("how do I bake a chocolate cake", db, top_k=5)
        assert res.found is False
        assert len(res.chunks) == 0
        assert res.below_threshold is True


class TestSmartAssessmentProductRelevanceGate:
    """
    Regression test suite for Smart Assessment product relevance and safety gate.
    Ensures that unrelated products (helmet, cement) never leak unrelated standards
    (such as chlorine tablets or sterilizers) and return insufficient evidence.
    """

    def test_domestic_pressure_cooker_assessment_retrieves_is2347(self, db):
        """1. Domestic pressure cooker -> correctly retrieves IS 2347 evidence."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")

        prompt = (
            "Analyze this product for BIS requirements using ONLY the retrieved official BIS evidence.\n\n"
            "Product: Domestic pressure cooker\n\n"
            "Return: 1. Product identified 2. Applicable Indian Standard(s)"
        )
        res = retrieve(prompt, db, top_k=3)
        assert res.found is True
        assert len(res.chunks) > 0
        top = res.chunks[0]
        assert "IS 2347" in top.content
        assert "Domestic Pressure Cookers" in top.content

    def test_helmet_assessment_returns_insufficient_evidence(self, db):
        """2. Helmet -> returns insufficient evidence when no helmet standards exist."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")

        prompt = (
            "Analyze this product for BIS requirements using ONLY the retrieved official BIS evidence.\n\n"
            "Product: helmet\n\n"
            "Return: 1. Product identified 2. Applicable Indian Standard(s)"
        )
        res = retrieve(prompt, db, top_k=3)
        assert res.found is False
        assert len(res.chunks) == 0
        assert res.below_threshold is True

    def test_cement_assessment_returns_insufficient_evidence(self, db):
        """3. Cement -> returns insufficient evidence when no cement standards exist."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")

        prompt = (
            "Analyze this product for BIS requirements using ONLY the retrieved official BIS evidence.\n\n"
            "Product: cement\n\n"
            "Return: 1. Product identified 2. Applicable Indian Standard(s)"
        )
        res = retrieve(prompt, db, top_k=3)
        assert res.found is False
        assert len(res.chunks) == 0
        assert res.below_threshold is True

    def test_chocolate_cake_assessment_returns_insufficient_evidence(self, db):
        """4. Chocolate cake -> returns insufficient BIS evidence."""
        if not _has_embeddings(db):
            pytest.skip("No embeddings in DB")

        prompt = (
            "Analyze this product for BIS requirements using ONLY the retrieved official BIS evidence.\n\n"
            "Product: chocolate cake\n\n"
            "Return: 1. Product identified 2. Applicable Indian Standard(s)"
        )
        res = retrieve(prompt, db, top_k=3)
        assert res.found is False
        assert len(res.chunks) == 0
        assert res.below_threshold is True

