"""
BIS Sahayak — Chat API Tests
Phase 8: FastAPI Chat API

Tests:
  1. Health check endpoint (GET /api/v1/health)
  2. Valid chat request with session generation
  3. Empty / whitespace message validation rejection (HTTP 422)
  4. Mode validation ('consumer', 'industry')
  5. Session reuse when passing existing session_id
  6. Relevant BIS query returns citations and found_information=True
  7. Irrelevant / out-of-scope query returns fallback response and found_information=False
  8. Database persistence for chat_sessions and chat_messages
"""

import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.main import app
from app.models.chat import ChatMessage, ChatSession


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_check_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "BIS Sahayak backend is running" in data["message"]
        assert "version" in data


class TestChatValidation:
    """Validation tests for POST /api/v1/chat."""

    def test_empty_message_rejected(self, client):
        response = client.post("/api/v1/chat", json={"message": "", "mode": "consumer"})
        assert response.status_code == 422

    def test_whitespace_only_message_rejected(self, client):
        response = client.post("/api/v1/chat", json={"message": "   \n\t  ", "mode": "consumer"})
        assert response.status_code == 422

    def test_invalid_mode_rejected(self, client):
        response = client.post(
            "/api/v1/chat",
            json={"message": "What is ISI?", "mode": "invalid_mode_value"},
        )
        assert response.status_code == 422

    def test_message_too_long_rejected(self, client):
        long_message = "A" * 2001
        response = client.post(
            "/api/v1/chat",
            json={"message": long_message, "mode": "consumer"},
        )
        assert response.status_code == 422


class TestChatSessionHandling:
    """Tests for chat session lifecycle."""

    def test_new_session_created_when_omitted(self, client, db_session):
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "What is the Bureau of Indian Standards?",
                "session_id": None,
                "mode": "consumer",
            },
        )
        assert response.status_code == 200
        data = response.json()
        session_id = data.get("session_id")
        assert session_id is not None
        # Verify valid UUID format
        parsed_uuid = uuid.UUID(session_id)
        assert parsed_uuid

        # Verify session exists in DB
        db_sess = db_session.query(ChatSession).filter(ChatSession.id == parsed_uuid).first()
        assert db_sess is not None
        assert db_sess.mode == "consumer"

    def test_existing_session_reused(self, client, db_session):
        # 1. Create a session via first message
        first_resp = client.post(
            "/api/v1/chat",
            json={"message": "What is BIS?", "mode": "consumer"},
        )
        assert first_resp.status_code == 200
        session_id = first_resp.json()["session_id"]

        # 2. Send follow-up using same session_id
        second_resp = client.post(
            "/api/v1/chat",
            json={
                "message": "How does certification work?",
                "session_id": session_id,
                "mode": "consumer",
            },
        )
        assert second_resp.status_code == 200
        assert second_resp.json()["session_id"] == session_id

        # Verify exactly two user messages in this session
        msgs = (
            db_session.query(ChatMessage)
            .filter(ChatMessage.session_id == uuid.UUID(session_id))
            .all()
        )
        # 2 user messages + 2 assistant messages = 4 messages
        assert len(msgs) == 4

    def test_malformed_session_id_handled_gracefully(self, client):
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Testing malformed session ID handling",
                "session_id": "not-a-valid-uuid",
                "mode": "consumer",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should create and return a valid UUID instead of crashing
        assert uuid.UUID(data["session_id"])


class TestChatRAGAndCitations:
    """RAG retrieval and citation grounding tests."""

    def test_relevant_query_returns_citations(self, client):
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
        assert len(data["citations"]) > 0

        # Validate citation schema and deduplication
        first_cit = data["citations"][0]
        assert first_cit["number"] == 1
        assert "title" in first_cit and first_cit["title"]
        assert "source_url" in first_cit and first_cit["source_url"].startswith("http")
        assert "hallmark" in first_cit["title"].lower() or "bis" in first_cit["title"].lower()

        # Ensure no debug / stub / internal RAG text is leaked in user answer
        assert "STUB LLM" not in data["answer"]
        assert "similarity=" not in data["answer"]
        assert "Retrieved sources:" not in data["answer"]

        # Ensure citations are deduplicated (1-3 unique sources max)
        source_urls = [c["source_url"] for c in data["citations"]]
        assert len(source_urls) == len(set(source_urls))
        assert len(data["citations"]) <= 3

    def test_unrelated_query_returns_fallback_and_no_citations(self, client):
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "How do I bake a chocolate sponge cake with strawberry frosting?",
                "mode": "consumer",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["found_information"] is False
        assert data["citations"] == []
        assert "couldn't find enough relevant information" in data["answer"].lower()


class TestMessagePersistence:
    """Database persistence verification."""

    def test_messages_persisted_with_citations(self, client, db_session):
        test_msg = "What is the procedure for consumer compensation in hallmarked gold?"
        response = client.post(
            "/api/v1/chat",
            json={"message": test_msg, "mode": "consumer"},
        )
        assert response.status_code == 200
        session_id = uuid.UUID(response.json()["session_id"])

        # Fetch messages for this session
        messages = (
            db_session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        assert len(messages) == 2
        user_m, asst_m = messages[0], messages[1]

        assert user_m.role == "user"
        assert user_m.content == test_msg

        assert asst_m.role == "assistant"
        assert asst_m.content == response.json()["answer"]
        if response.json()["found_information"]:
            assert asst_m.citations is not None
            assert len(asst_m.citations) == len(response.json()["citations"])
