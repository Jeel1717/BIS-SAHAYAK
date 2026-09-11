import os
from pathlib import Path
_env = Path(".env")
if _env.exists():
    for _line in _env.read_text("utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            k, _, v = _line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

import sys
sys.path.insert(0, ".")
from app.database import SessionLocal
from sqlalchemy import text

s = SessionLocal()
rows = s.execute(text("""
    SELECT c.id, d.title, d.standard_number, c.chunk_title, c.content
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    WHERE c.content ILIKE '%2347%' OR c.content ILIKE '%pressure cooker%'
""")).fetchall()

print(f"Found {len(rows)} matching chunks:")
for r in rows:
    print("=" * 60)
    print(f"Doc: {r.title} | Std: {r.standard_number} | ChunkTitle: {r.chunk_title}")
    print(f"Content:\n{r.content}")


s.close()
