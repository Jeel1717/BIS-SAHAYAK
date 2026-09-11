"""
BIS Sahayak — Chat Router
Phase 8: FastAPI Chat API

POST /api/v1/chat
Connects: Frontend → FastAPI → RAG retrieval → Context Builder → LLM Interface → Response + Citations
"""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.chat import ChatMessage, ChatSession
from app.rag.context_builder import build_context
from app.rag.llm_interface import (
    LLMConfigurationError,
    LLMQuotaError,
    LLMRuntimeError,
    get_llm,
)
from app.rag.retriever import retrieve
from app.schemas.chat import ChatRequest, ChatResponse, CitationItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])

NO_INFO_FALLBACK = (
    "I couldn't find enough relevant information in the BIS sources available to me "
    "to answer that confidently. Please visit https://www.bis.gov.in or contact BIS at 1800-11-4000."
)


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to BIS Sahayak",
    description="Processes user questions using the local RAG pipeline with grounded citations.",
)
def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    RAG-powered chat endpoint with anonymous session support and grounded citations.
    """
    # ── 1. Session resolution ──────────────────────────────────────────────────
    session: Optional[ChatSession] = None

    if request.session_id:
        try:
            session_uuid = uuid.UUID(request.session_id)
            session = db.query(ChatSession).filter(ChatSession.id == session_uuid).first()
            if not session:
                # Specified UUID doesn't exist yet; create it
                session = ChatSession(id=session_uuid, mode=request.mode.value)
                db.add(session)
                db.commit()
                db.refresh(session)
                logger.info("Created new session with provided ID: %s", session.id)
            else:
                logger.info("Reusing existing session: %s", session.id)
        except (ValueError, TypeError, AttributeError):
            # Gracefully handle malformed UUID strings by creating a fresh session
            session = ChatSession(mode=request.mode.value)
            db.add(session)
            db.commit()
            db.refresh(session)
            logger.warning(
                "Invalid session_id %r provided; created fresh session: %s",
                request.session_id,
                session.id,
            )
    else:
        # No session_id supplied; generate a new session
        session = ChatSession(mode=request.mode.value)
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info("Created new session: %s", session.id)

    # ── 2. Persist user message ───────────────────────────────────────────────
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
        citations=None,
    )
    db.add(user_msg)

    # ── 3. RAG Retrieval & Context Building ───────────────────────────────────
    retrieval_result = retrieve(query=request.message, db=db)
    context = build_context(retrieval_result)

    # ── 4. Safety & Grounding Check ───────────────────────────────────────────
    # If retrieval found no relevant BIS information, return fallback immediately
    # without calling the LLM (saves API quota and prevents hallucinations).
    if not retrieval_result.found or not context.has_information:
        found_information = False
        answer = NO_INFO_FALLBACK
        citations = []
    else:
        # ── 5. LLM Completion & Error Handling ────────────────────────────────
        try:
            llm = get_llm()
            answer = llm.complete(context)
            found_information = True
            citations = [
                CitationItem(
                    number=i,
                    title=chunk.document_title,
                    source_url=chunk.source_url,
                    clause_number=chunk.clause_number,
                    page_number=chunk.page_number,
                )
                for i, chunk in enumerate(context.source_chunks, start=1)
            ]
        except LLMConfigurationError as exc:
            logger.error("LLM configuration error: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            )
        except LLMQuotaError as exc:
            logger.warning("LLM quota error: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="BIS Sahayak is currently experiencing high demand on the free tier. Please try again in a few moments.",
            )
        except LLMRuntimeError as exc:
            logger.error("LLM runtime error: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to generate response from BIS Sahayak at this time. Please try again.",
            )

    # ── 6. Persist assistant message ──────────────────────────────────────────
    citations_data = [c.model_dump() for c in citations] if citations else None
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
        citations=citations_data,
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        session_id=str(session.id),
        answer=answer,
        citations=citations,
        found_information=found_information,
    )
