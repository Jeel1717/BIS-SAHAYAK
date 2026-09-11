"""
BIS Sahayak — Document & Chunk Models
Phase 5 / Chapter 14: Database Schema

Tables:
  - documents  : BIS Standard documents (metadata only)
  - chunks     : Text chunks extracted from documents, with pgvector embeddings
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, EMBEDDING_DIMENSION


class Document(Base):
    """
    A BIS Standard document (e.g. IS 14543, IS 16700).

    Stores document-level metadata only.
    The actual text content lives in the related Chunk rows.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # Human-readable title, e.g. "Packaged Drinking Water — Specification"
    title: Mapped[str] = mapped_column(String, nullable=False)

    # BIS standard number, e.g. "IS 14543"
    standard_number: Mapped[str | None] = mapped_column(String, nullable=True)

    # URL where the document was fetched from
    source_url: Mapped[str] = mapped_column(String, nullable=False)

    # e.g. "Indian Standard", "BIS Regulation", "FAQ"
    document_type: Mapped[str | None] = mapped_column(String, nullable=True)

    # Version string or effective date string, e.g. "2016", "April 2021"
    version_or_effective_date: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # One document has many chunks
    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} standard_number={self.standard_number!r}>"


class Chunk(Base):
    """
    A text chunk extracted from a Document page/section.

    The `embedding` column stores a pgvector Vector that enables
    similarity search (cosine / L2 distance) for RAG retrieval.
    The vector dimension is controlled by EMBEDDING_DIMENSION in .env.
    """

    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The raw text of this chunk
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Section heading / title for this chunk (e.g. "Consumer Protection", "HUID Verification")
    # Helps retrieval context and citation display.
    chunk_title: Mapped[str | None] = mapped_column(String, nullable=True)

    # BIS clause number, e.g. "4.3.1" (nullable — not all docs have clauses)
    clause_number: Mapped[str | None] = mapped_column(String, nullable=True)

    # Page number in the original PDF (nullable)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # pgvector embedding — dimension set via EMBEDDING_DIMENSION env variable
    # This column is nullable: chunks can exist before they are embedded.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSION),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Many chunks belong to one document
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return (
            f"<Chunk id={self.id} "
            f"document_id={self.document_id} "
            f"page={self.page_number}>"
        )
