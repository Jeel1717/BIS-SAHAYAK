"""
BIS Sahayak — Chapter 14 Retrieval and Answer Quality Verification
Tests all required questions across Consumer, Hallmarking, Industry, Product, and Out-of-Scope categories.
"""

import sys
import io
sys.path.insert(0, ".")

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_CASES = [
    # ── CONSUMER ─────────────────────────────────────────────────────────────
    ("CONSUMER", "How do I verify hallmarked gold?", True),
    ("CONSUMER", "What is HUID?", True),
    ("CONSUMER", "How can I check whether a product is BIS certified?", True),
    ("CONSUMER", "What does the ISI mark mean?", True),
    ("CONSUMER", "How can I file a BIS-related complaint?", True),

    # ── HALLMARKING ──────────────────────────────────────────────────────────
    ("HALLMARKING", "What is an Assaying and Hallmarking Centre?", True),
    ("HALLMARKING", "How does HUID verification work?", True),
    ("HALLMARKING", "What is silver hallmarking?", True),

    # ── INDUSTRY ─────────────────────────────────────────────────────────────
    ("INDUSTRY", "How can a manufacturer obtain BIS certification?", True),
    ("INDUSTRY", "How do I find the applicable Indian Standard?", True),
    ("INDUSTRY", "What is conformity assessment?", True),
    ("INDUSTRY", "What happens during BIS testing and inspection?", True),

    # ── PRODUCT ──────────────────────────────────────────────────────────────
    ("PRODUCT", "What BIS requirements apply to pressure cookers?", True),
    ("PRODUCT", "How can I determine whether certification is compulsory?", True),

    # ── OUT OF SCOPE ─────────────────────────────────────────────────────────
    ("OUT_OF_SCOPE", "How do I bake a chocolate cake?", False),
    ("OUT_OF_SCOPE", "Tell me a joke.", False),
]

def main():
    print("=" * 80)
    print("BIS Sahayak — Chapter 14 Retrieval & Grounding Evaluation")
    print("=" * 80)

    passed_count = 0
    total_count = len(TEST_CASES)

    for category, query, expected_found in TEST_CASES:
        mode = "industry" if category == "INDUSTRY" else "consumer"
        res = client.post("/api/v1/chat", json={"message": query, "mode": mode})
        if res.status_code != 200:
            print(f"[FAIL] HTTP {res.status_code} for query: {query}")
            continue

        data = res.json()
        found = data.get("found_information", False)
        answer = data.get("answer", "")
        citations = data.get("citations", [])

        # Checks:
        is_ok = (found == expected_found)

        # Ensure no leaked debug strings
        leaks = [s for s in ["STUB LLM", "similarity=", "Retrieved sources:", "cosine distance"] if s in answer]
        if leaks:
            is_ok = False

        status_tag = "[PASS]" if is_ok else "[FAIL]"
        if is_ok:
            passed_count += 1

        print(f"\n{status_tag} [{category}] Query: {query}")
        print(f"       Found: {found} (Expected: {expected_found}) | Citations: {len(citations)}")
        if citations:
            for c in citations:
                print(f"       -> [{c['number']}] {c['title'][:55]} ({c['source_url']})")
        print(f"       Answer snippet: {answer[:140].replace(chr(10), ' ')}...")
        if leaks:
            print(f"       LEAK DETECTED: {leaks}")

    print("\n" + "=" * 80)
    print(f"EVALUATION SUMMARY: {passed_count} / {total_count} PASSED")
    print("=" * 80)

    if passed_count != total_count:
        sys.exit(1)

if __name__ == "__main__":
    main()
