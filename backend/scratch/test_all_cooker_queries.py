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
from scratch.prototype_retrieval import hybrid_retrieve, SessionLocal

ALL_COOKER_QUERIES = [
    "cooker",
    "pressure cooker",
    "pressure cookers",
    "pressure cooking",
    "BIS cooker",
    "BIS pressure cooker",
    "cooker BIS mark",
    "cooker certification",
    "pressure cooker certification",
    "pressure cooker standard",
    "standard for pressure cooker",
    "IS 2347",
    "requirements for pressure cooker",
    "requirements for pressure cookers",
    "which IS standard applies to pressure cooker",
    "what BIS standard is for cooker",
    "is BIS certification mandatory for pressure cooker",
    "does pressure cooker need BIS certification",
    "BIS requirements for cooker",
    "pressure cooker testing",
    "pressure cooker licence",
    "manufacturer of pressure cooker",
    "pressure cooker compliance",
    "pressure cooker ISI mark"
]

s = SessionLocal()
all_passed = True
print(f"Testing {len(ALL_COOKER_QUERIES)} cooker query variations:")
print("=" * 80)
for i, q in enumerate(ALL_COOKER_QUERIES, 1):
    res = hybrid_retrieve(q, s, top_k=3)
    if not res:
        print(f"[{i:02d}] FAILED: '{q}' -> 0 results!")
        all_passed = False
        continue
    top = res[0]
    has_cooker = "cooker" in top["content"].lower() or "2347" in top["content"]
    has_is2347 = "2347" in top["content"]
    status = "PASS" if has_cooker else "FAIL"
    if not has_cooker:
        all_passed = False
    print(f"[{i:02d}] [{status}] '{q}' -> Top: {top['document_title'][:40]} (Score: {top['final_score']:.3f}, IS2347: {has_is2347})")

NON_COOKER_QUERIES = [
    ("what is HUID", "huid"),
    ("how do I verify hallmarked gold", "hallmarking"),
    ("how can a manufacturer obtain BIS certification", "certification"),
    ("how do I bake a chocolate cake", "cake"),
]

print("\nTesting Non-Cooker Regression Queries:")
print("=" * 80)
for q, expected_topic in NON_COOKER_QUERIES:
    res = hybrid_retrieve(q, s, top_k=3)
    if expected_topic == "cake":
        status = "PASS" if len(res) == 0 else "FAIL"
        print(f"[{status}] '{q}' -> {len(res)} results (Expected 0 / out-of-scope fallback)")
        if len(res) > 0:
            all_passed = False
    else:
        has_cooker = any("cooker" in r["content"].lower() or "2347" in r["content"] for r in res)
        status = "PASS" if (len(res) > 0 and not has_cooker) else "FAIL"
        top_doc = res[0]["document_title"] if res else "None"
        print(f"[{status}] '{q}' -> Top: {top_doc[:45]} (CookerLeaked: {has_cooker})")
        if not (len(res) > 0 and not has_cooker):
            all_passed = False

print("=" * 80)
if all_passed:
    print("ALL 24 COOKER + 4 NON-COOKER REGRESSION TESTS PASSED!")
else:
    print("SOME TESTS FAILED")
s.close()
