"""
BIS Sahayak — RAG Package
Phase 7: Retrieval-Augmented Generation

Modules:
  embedder.py       — local sentence-transformers embedding service
  retriever.py      — pgvector similarity search
  context_builder.py — formats retrieved chunks into LLM-ready context
  llm_interface.py  — abstract LLM interface (not connected to paid API)
"""
