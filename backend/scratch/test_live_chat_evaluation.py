import urllib.request
import json
import sys

queries = [
    "What BIS requirements apply to pressure cookers?",
    "cooker",
    "What is HUID?",
    "How can a manufacturer obtain BIS certification?",
    "How do I bake a chocolate cake?",
]

for q in queries:
    print("=" * 80)
    print("QUERY:", q)
    req_data = json.dumps({"message": q, "mode": "consumer"}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/chat",
        data=req_data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            res = json.loads(resp.read().decode())
            print("STATUS:", resp.status)
            answer = res.get("answer", "")
            clean_answer = answer[:600].encode("ascii", "replace").decode("ascii")
            print("ANSWER SNIPPET:\n", clean_answer)
            print("...")
            citations = res.get("citations", [])
            print("TOTAL CITATIONS:", len(citations))
            for c in citations:
                clean_title = c.get("title", "").encode("ascii", "replace").decode("ascii")
                clause = c.get("clause_number") or "N/A"
                print(f"  - [{c.get('number')}] {clean_title} | Clause: {clause}")
    except Exception as e:
        print("ERROR:", e)

print("=" * 80)
