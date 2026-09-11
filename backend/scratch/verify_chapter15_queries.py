"""
BIS Sahayak — Chapter 15 Real Queries Verification Script
Verifies 12 real user queries against the live /api/v1/chat endpoint:
1. How do I verify hallmarked gold?
2. What is HUID?
3. How can I check whether a product is BIS certified?
4. What does the ISI mark mean?
5. How can I file a BIS-related complaint?
6. What is an Assaying and Hallmarking Centre?
7. What is silver hallmarking?
8. How can a manufacturer obtain BIS certification?
9. How do I find the applicable Indian Standard?
10. What BIS requirements apply to pressure cookers?
11. How can I determine whether certification is compulsory?
12. How do I bake a chocolate cake? (Out of scope)
"""

import urllib.request
import json
import time

QUERIES = [
    ("How do I verify hallmarked gold?", True, "consumer"),
    ("What is HUID?", True, "consumer"),
    ("How can I check whether a product is BIS certified?", True, "consumer"),
    ("What does the ISI mark mean?", True, "consumer"),
    ("How can I file a BIS-related complaint?", True, "consumer"),
    ("What is an Assaying and Hallmarking Centre?", True, "consumer"),
    ("What is silver hallmarking?", True, "consumer"),
    ("How can a manufacturer obtain BIS certification?", True, "industry"),
    ("How do I find the applicable Indian Standard?", True, "industry"),
    ("What BIS requirements apply to pressure cookers?", True, "consumer"),
    ("How can I determine whether certification is compulsory?", True, "industry"),
    ("How do I bake a chocolate cake?", False, "consumer"),
]

def run():
    print("=" * 70)
    print("CHAPTER 15 — LIVE RAG & ANSWER VERIFICATION (12 QUERIES)")
    print("=" * 70)

    url = "http://127.0.0.1:8000/api/v1/chat"
    all_passed = True

    for i, (q, should_find, mode) in enumerate(QUERIES, 1):
        payload = json.dumps({"message": q, "mode": mode}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[{i}/12] FAILED to call API: {e}")
            all_passed = False
            continue

        found_info = data.get("found_information", False)
        answer = data.get("answer", "")
        citations = data.get("citations", [])

        # Quality checks
        has_debug = any(k in answer.lower() for k in ["similarity=", "chunk_id", "vector", "score:"])
        
        status_ok = True
        notes = []

        if should_find:
            if not found_info:
                status_ok = False
                notes.append("Expected found_information=True, got False")
            if len(citations) == 0:
                status_ok = False
                notes.append("Expected citations > 0, got 0")
        else:
            if found_info:
                status_ok = False
                notes.append("Expected found_information=False for out-of-scope query")
            if len(citations) > 0:
                status_ok = False
                notes.append(f"Expected 0 citations for out-of-scope, got {len(citations)}")

        if has_debug:
            status_ok = False
            notes.append("Found debug text in answer!")

        if not status_ok:
            all_passed = False

        status_str = "PASS" if status_ok else "FAIL"
        print(f"\nQuery {i}/12 [{status_str}]: \"{q}\"")
        print(f"  Mode: {mode} | Found Info: {found_info} | Citations: {len(citations)}")
        for c in citations:
            print(f"    [{c['number']}] {c['title']} ({c['source_url']})")
        print(f"  Answer sample (first 180 chars):\n    {answer[:180]}...")
        if notes:
            print(f"  ISSUES: {', '.join(notes)}")

        time.sleep(0.5)

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL 12 VERIFICATION QUERIES PASSED WITH ZERO ERRORS!")
    else:
        print("SOME QUERIES FAILED VERIFICATION")
    print("=" * 70)

if __name__ == "__main__":
    run()
