import urllib.request
import json
import sys

print("=== 1. Testing Frontend HTML on localhost:3000 ===")
try:
    with urllib.request.urlopen("http://localhost:3000") as resp:
        html = resp.read().decode("utf-8")
        assert "Find My BIS Requirements" in html, "Missing Find My BIS Requirements"
        assert "Describe your product" in html, "Missing Describe your product"
        assert "Analyze Product" in html, "Missing Analyze Product"
        assert "BIS Smart Assessment" in html, "Missing BIS Smart Assessment"
        print("[PASS] Frontend successfully serves Smart Assessment UI elements!")
except Exception as e:
    print("[FAIL] Frontend check:", e)
    sys.exit(1)

print("\n=== 2. Testing Smart Assessment via Backend API ===")
prompt = """Analyze this product for BIS requirements using ONLY the retrieved official BIS evidence.

Product: Domestic pressure cooker

Return:
1. Product identified
2. Applicable Indian Standard(s)
3. BIS certification scheme/pathway
4. Procedure, if explicitly supported
5. Evidence/source
6. Recommended next action

Do not invent facts. If evidence is insufficient, say so."""

url = "http://127.0.0.1:8000/api/v1/chat"
req = urllib.request.Request(
    url,
    data=json.dumps({"message": prompt, "mode": "industry"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    ans = data["answer"]
    print("Found info:", data["found_information"])
    print("Citations:", len(data.get("citations", [])))
    print("Answer snippet:\n", ans)
    assert "IS 2347" in ans, "Expected IS 2347 in answer"
    assert "Domestic Pressure Cookers" in ans, "Expected Domestic Pressure Cookers in answer"
    assert "Scheme I" in ans, "Expected Scheme I in answer"
    assert "Simplified Procedure" in ans, "Expected Simplified Procedure in answer"
    assert "187" in ans, "Expected 187 in answer"
    print("[PASS] Backend returned evidence-backed assessment data!")

print("\n=== 3. Testing Standard Chat API (Existing Chat Unchanged) ===")
chat_queries = [
    ("What BIS requirements apply to pressure cookers?", True),
    ("What is HUID?", True),
    ("How do I bake a chocolate cake?", False)
]
for q, expected_found in chat_queries:
    req = urllib.request.Request(
        url,
        data=json.dumps({"message": q, "mode": "consumer"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        found = res["found_information"]
        c_count = len(res.get("citations", []))
        print(f"Query: '{q}' -> found_information={found}, citations={c_count}")
        assert found == expected_found, f"Expected found={expected_found} for '{q}', got {found}"
        print(f"  [PASS] Verified chat response: {res['answer'][:100]}...")

print("\n============================================================")
print("SUCCESS: ALL FRONTEND AND BACKEND VERIFICATIONS PASSED!")
print("============================================================")
