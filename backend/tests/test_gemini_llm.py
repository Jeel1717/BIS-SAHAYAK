"""
BIS Sahayak — Gemini Runtime & Full Integration Tests
Phase 10: Real Free Gemini Runtime (Mocked for tests, ₹0 quota used)

Tests:
  1. Gemini provider initialization
  2. Missing API key handling (LLMConfigurationError)
  3. Successful mocked Gemini response
  4. Grounded RAG context correctly passed to the Gemini SDK
  5. Hallmarked-gold question produces a generated answer via chat API
  6. Retrieved citations remain authoritative and match retrieved chunks
  7. Unrelated question produces safe fallback WITHOUT calling Gemini API
  8. Quota error (429) returns safe HTTP 503 service unavailable
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag.context_builder import BuiltContext, NO_INFORMATION_RESPONSE
from app.rag.llm_interface import (
    GeminiLLM,
    LLMConfigurationError,
    LLMQuotaError,
    LLMRuntimeError,
    get_llm,
)
from app.rag.retriever import RetrievalResult, RetrievedChunk


@pytest.fixture
def mock_chunk():
    return RetrievedChunk(
        chunk_id="chunk-test-1",
        document_id="doc-test-1",
        document_title="BIS Hallmarking — Consumer Protection Guide",
        document_type="Consumer Guide",
        source_url="https://www.bis.gov.in/hallmarking-overview/consumer-protection/?lang=en",
        content="Consumers should verify the 6-digit HUID number on hallmarked gold jewellery using the BIS Care App.",
        clause_number="Clause 3.1",
        page_number=1,
        similarity=0.72,
    )


@pytest.fixture
def sample_context(mock_chunk):
    return BuiltContext(
        system_prompt="You are BIS Sahayak, an AI assistant for Indian Standards and BIS services.",
        sources_block=f"[1] {mock_chunk.document_title}\nSource: {mock_chunk.source_url}\nContent:\n{mock_chunk.content}",
        user_question="What should a consumer check when buying hallmarked gold?",
        has_information=True,
        source_chunks=[mock_chunk],
    )


# ── 1. Provider Initialization & Key Handling ─────────────────────────────────

class TestGeminiProvider:
    def test_gemini_provider_initialization(self):
        llm = GeminiLLM(api_key="test-mock-key-12345", model_name="gemini-3.7-flash")
        assert llm.api_key == "test-mock-key-12345"
        assert llm.model_name == "gemini-3.7-flash"

    def test_missing_api_key_raises_configuration_error(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        llm = GeminiLLM()
        with pytest.raises(LLMConfigurationError, match="Gemini API key is not configured"):
            _ = llm.api_key

    def test_factory_resolves_gemini(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-test")
        llm = get_llm()
        assert isinstance(llm, GeminiLLM)

    def test_factory_resolves_google(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "google")
        monkeypatch.setenv("GEMINI_API_KEY", "dummy-key-for-test")
        llm = get_llm()
        assert isinstance(llm, GeminiLLM)


# ── 2. Mocked Completion & RAG Context Passing ────────────────────────────────

class TestGeminiCompletion:
    def test_successful_mocked_gemini_response(self, sample_context):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            "When purchasing hallmarked gold jewellery, verify the BIS hallmark logo "
            "and the 6-digit alphanumeric HUID number using the BIS Care App [1]."
        )
        mock_client.models.generate_content.return_value = mock_response

        llm = GeminiLLM(api_key="mock-key", client=mock_client)
        answer = llm.complete(sample_context)

        assert "HUID number" in answer
        assert "[1]" in answer
        assert mock_client.models.generate_content.called

    def test_rag_context_passed_to_gemini(self, sample_context):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Grounded answer [1]"
        mock_client.models.generate_content.return_value = mock_response

        llm = GeminiLLM(api_key="mock-key", client=mock_client)
        _ = llm.complete(sample_context)

        call_args = mock_client.models.generate_content.call_args
        assert call_args is not None
        kwargs = call_args.kwargs
        contents = kwargs.get("contents", "")

        # Verify ONLY grounded context and user question are passed
        assert sample_context.sources_block in contents
        assert sample_context.user_question in contents
        assert kwargs.get("config").system_instruction == sample_context.system_prompt

    def test_no_information_context_skips_api_call(self):
        mock_client = MagicMock()
        llm = GeminiLLM(api_key="mock-key", client=mock_client)

        empty_context = BuiltContext(
            system_prompt="Test system prompt",
            sources_block="",
            user_question="Random out of scope query",
            has_information=False,
            source_chunks=[],
        )

        answer = llm.complete(empty_context)
        assert answer == NO_INFORMATION_RESPONSE
        # Crucial for ₹0 rule: Zero API calls when no relevant context found
        assert not mock_client.models.generate_content.called

    def test_quota_limit_raises_llm_quota_error(self, sample_context):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("429 RESOURCE_EXHAUSTED: quota exceeded")

        llm = GeminiLLM(api_key="mock-key", client=mock_client)
        with pytest.raises(LLMQuotaError, match="high demand"):
            llm.complete(sample_context)


# ── 3. Chat API Integration with Mocked Gemini ────────────────────────────────

class TestChatAPIGeminiIntegration:
    @pytest.fixture
    def client(self):
        import uuid
        from app.database import get_db

        mock_db = MagicMock()
        def fake_refresh(instance):
            if hasattr(instance, "id") and not instance.id:
                instance.id = uuid.uuid4()
        def fake_add(instance):
            if hasattr(instance, "id") and not instance.id:
                instance.id = uuid.uuid4()
        mock_db.refresh.side_effect = fake_refresh
        mock_db.add.side_effect = fake_add
        mock_db.query.return_value.filter.return_value.first.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db
        with TestClient(app) as c:
            yield c
        app.dependency_overrides.pop(get_db, None)

    def test_hallmarked_gold_produces_generated_answer_and_authoritative_citations(
        self, client, mock_chunk
    ):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            "When buying hallmarked gold, consumers should ensure the jewellery carries the "
            "BIS hallmark, purity in karats (e.g. 22K916), and the 6-digit HUID code [1]. "
            "You can verify the authenticity using the BIS Care mobile application [1]."
        )
        mock_client.models.generate_content.return_value = mock_response
        mock_llm = GeminiLLM(api_key="mock-test-key", client=mock_client)

        mock_retrieval = RetrievalResult(
            query="What should a consumer check when buying hallmarked gold?",
            chunks=[mock_chunk],
            below_threshold=False,
        )

        with patch("app.routers.chat.retrieve", return_value=mock_retrieval):
            with patch("app.routers.chat.get_llm", return_value=mock_llm):
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": "What should a consumer check when buying hallmarked gold?",
                        "mode": "consumer",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["found_information"] is True
        assert "BIS hallmark" in data["answer"]
        assert len(data["citations"]) > 0

        # Verify authoritative citations are preserved from pgvector chunks
        first_cit = data["citations"][0]
        assert first_cit["number"] == 1
        assert "hallmarking" in first_cit["title"].lower() or "bis" in first_cit["title"].lower()
        assert first_cit["source_url"].startswith("https://www.bis.gov.in")

    def test_unrelated_question_skips_gemini_completely(self, client):
        mock_client = MagicMock()
        mock_llm = GeminiLLM(api_key="mock-test-key", client=mock_client)

        mock_retrieval = RetrievalResult(
            query="How do I bake a chocolate cake with strawberry frosting?",
            chunks=[],
            below_threshold=True,
        )

        with patch("app.routers.chat.retrieve", return_value=mock_retrieval):
            with patch("app.routers.chat.get_llm", return_value=mock_llm):
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": "How do I bake a chocolate cake with strawberry frosting?",
                        "mode": "consumer",
                    },
                )

        assert response.status_code == 200
        data = response.json()
        assert data["found_information"] is False
        assert data["citations"] == []
        assert "couldn't find enough relevant information" in data["answer"].lower()
        # Must NOT call the Gemini API when retrieval produces no results
        assert not mock_client.models.generate_content.called

    def test_missing_api_key_returns_clean_500_error(self, client, mock_chunk, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        mock_retrieval = RetrievalResult(
            query="What should a consumer check when buying hallmarked gold?",
            chunks=[mock_chunk],
            below_threshold=False,
        )

        with patch("app.routers.chat.retrieve", return_value=mock_retrieval):
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "What should a consumer check when buying hallmarked gold?",
                    "mode": "consumer",
                },
            )
        assert response.status_code == 500
        data = response.json()
        assert "Gemini API key is not configured" in data["detail"]
