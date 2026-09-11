import os, sys
from pathlib import Path
_env = Path(".env")
if _env.exists():
    for _line in _env.read_text("utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            k, _, v = _line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, ".")
from app.database import SessionLocal
from app.rag.retriever import retrieve

s = SessionLocal()
res = retrieve("cooker", s)
print(f"Query 'cooker' -> Found: {res.found}, Chunks: {len(res.chunks)}")
for i, c in enumerate(res.chunks, 1):
    print(f"[{i}] Sim: {c.similarity:.4f} | Doc: {c.document_title} | Clause: {c.clause_number}")
    print(f"    Excerpt: {c.content[:140].strip().replace('\n', ' ')}...")

s.close()
