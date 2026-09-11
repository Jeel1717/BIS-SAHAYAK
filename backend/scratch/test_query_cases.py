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

TEST_QUERIES = [
    "cooker",
    "pressure cooker",
    "cooker certification",
    "what BIS standard applies to pressure cooker",
    "does pressure cooker need BIS certification",
    "What BIS requirements apply to pressure cookers?",
    "what is HUID",
    "how do I verify hallmarked gold",
    "how can a manufacturer obtain BIS certification",
    "how do I bake a chocolate cake"
]

s = SessionLocal()
print("CURRENT RETRIEVAL BASELINE:")
print("=" * 80)
for q in TEST_QUERIES:
    res = retrieve(q, s, top_k=5)
    print(f"\nQUERY: \"{q}\" -> Found: {res.found}, Total chunks: {len(res.chunks)}")
    if res.chunks:
        for i, c in enumerate(res.chunks[:3], 1):
            has_cooker = "cooker" in c.content.lower() or "2347" in c.content
            print(f"  [{i}] Sim: {c.similarity:.4f} | HasCooker/2347: {has_cooker} | Doc: {c.document_title[:45]} | Excerpt: {c.content[:80].strip().replace(chr(10), ' ')}...")
    else:
        print("  (No chunks returned / below threshold)")
s.close()
