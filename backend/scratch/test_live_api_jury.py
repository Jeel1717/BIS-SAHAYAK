import urllib.request
import json
import sys

queries = [
    ("What BIS requirements apply to pressure cookers?", "consumer"),
    ("What is HUID?", "consumer"),
    ("How do I verify hallmarked gold?", "consumer"),
    ("How can a manufacturer obtain BIS certification?", "industry"),
    ("How do I bake a chocolate cake?", "consumer"),
]

url = "http://127.0.0.1:8000/api/v1/chat"

for q, mode in queries:
    req_data = json.dumps({"message": q, "mode": mode}).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print("=" * 60)
            print(f"USER QUERY: {q} (mode={mode})")
            print(f"FOUND INFO: {res.get('found_information')}")
            print(f"CITATIONS COUNT: {len(res.get('citations', []))}")
            print("ANSWER:")
            print(res.get("answer"))
            print("CITATIONS:")
            for c in res.get("citations", []):
                print(f"  [{c['number']}] {c['title']} ({c['source_url']})")
            print()
    except Exception as e:
        print(f"Error on {q}: {e}")
