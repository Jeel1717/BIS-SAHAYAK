"""
BIS Sahayak — Models package
Phase 5: Database Schema

Importing this package registers all models with SQLAlchemy's Base
so that Base.metadata.create_all() can create every table in one call.
"""

from app.models.document import Chunk, Document
from app.models.chat import ChatMessage, ChatSession

__all__ = [
    "Document",
    "Chunk",
    "ChatSession",
    "ChatMessage",
]
