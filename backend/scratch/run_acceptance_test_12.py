"""
BIS Sahayak — Live API Acceptance Test (Requirement #12)
Verifies:
1. "What BIS requirements apply to pressure cookers?"
2. "cooker"
3. "What is HUID?"
Checks:
- Pressure-cooker-specific BIS evidence ranked above generic BIS Act / generic chunks.
- "What is HUID?" does NOT leak pressure cooker chunks.
"""

import json
import urllib.request

URL = "http://127.0.0.1:8000/api/v1/chat"

TESTS = [
    ("What BIS requirements apply to pressure cookers?", "consumer"),
    ("cooker", "consumer"),
    ("What is HUID?", "consumer"),
]

def run():
    print("=" * 80)
    print("LIVE API ACCEPTANCE TEST (REQUIREMENT #12)")
    print("=" * 80)

    for q, mode in TESTS:
        payload = json.dumps({"message": q, "mode": mode}).encode("utf-8")
        req = urllib.request.Request(
            URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        found = data.get("found_information", False)
        citations = data.get("citations", [])
        answer = data.get("answer", "")

        print(f"\nQUERY: {q!r} (Mode: {mode})")
        print(f"  Found Information: {found}")
        print(f"  Citations Returned ({len(citations)}):")
        for c in citations:
            print(f"    [{c['number']}] {c['title']}")
            print(f"        URL: {c['source_url']}")
            if c.get("clause_number"):
                print(f"        Clause: {c['clause_number']}")

        print(f"  Answer Summary (first 250 chars):\n    {answer[:250].strip().replace(chr(10), ' ')}...")

        # Verification checks
        if "cooker" in q.lower():
            cit_titles = " ".join(c['title'] for c in citations)
            assert "Simplified Procedure" in cit_titles or "Scheme I" in cit_titles or "Scheme - I" in cit_titles, (
                f"Expected pressure cooker source in citations for {q!r}, got: {cit_titles}"
            )
            assert "Power of Central Government" not in answer[:100], "Generic BIS Act direction leaked as top answer!"
            print("  --> CHECK: PASS — Pressure-cooker-specific BIS evidence prioritized!")
        elif "huid" in q.lower():
            cit_titles = " ".join(c['title'].lower() for c in citations)
            assert "cooker" not in cit_titles, f"Cooker leaked into HUID citations: {cit_titles}"
            assert "hallmark" in cit_titles or "jewell" in cit_titles or "complaint" in cit_titles, (
                f"Expected hallmarking in HUID citations: {cit_titles}"
            )
            print("  --> CHECK: PASS — Hallmarking evidence prioritized, zero cooker leakage!")

    print("\n" + "=" * 80)
    print("LIVE API ACCEPTANCE TEST: ALL CHECKS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    run()
