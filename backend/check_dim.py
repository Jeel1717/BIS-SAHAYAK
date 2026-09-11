import os, sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

_e = Path(".env")
if _e.exists():
    for l in _e.read_text("utf-8").splitlines():
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, _, v = l.partition("="); os.environ.setdefault(k.strip(), v.strip())

from sqlalchemy import text
from app.database import engine

with engine.connect() as c:
    r = c.execute(text(
        "SELECT atttypmod FROM pg_attribute WHERE attrelid='chunks'::regclass AND attname='embedding'"
    )).fetchone()
    print("Current embedding column atttypmod (= dimension):", r[0] if r else "not found")

    r2 = c.execute(text("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL")).scalar()
    print("Chunks with embeddings:", r2)

    r3 = c.execute(text("SELECT COUNT(*) FROM chunks")).scalar()
    print("Total chunks:", r3)
