"""
BIS Sahayak — Ingestion Package
Phase 6: BIS Knowledge Base

Modules:
  fetcher.py   — download HTML pages and PDFs from URLs
  extractor.py — extract clean text from HTML or PDF bytes
  chunker.py   — split text into ~300-500 token chunks
  pipeline.py  — orchestrate fetch → extract → chunk → DB insert
"""
