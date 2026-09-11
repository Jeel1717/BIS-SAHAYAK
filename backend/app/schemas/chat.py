"""
BIS Sahayak — Chat API Schemas
Phase 8: FastAPI Chat API
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ChatMode(str, Enum):
    CONSUMER = "consumer"
    INDUSTRY = "industry"


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question or query about Indian Standards and BIS services",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional UUID of an existing chat session",
    )
    mode: ChatMode = Field(
        default=ChatMode.CONSUMER,
        description="Assistant mode: 'consumer' or 'industry'",
    )

    @field_validator("message")
    @classmethod
    def message_not_empty_or_whitespace(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("message must not be empty or whitespace only")
        return trimmed


class CitationItem(BaseModel):
    number: int
    title: str
    source_url: str
    clause_number: Optional[str] = None
    page_number: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[CitationItem]
    found_information: bool
