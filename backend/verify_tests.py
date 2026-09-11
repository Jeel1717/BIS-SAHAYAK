"""
BIS Sahayak — Chapter 13 Verification Script
Runs Tests 2 through 6 using FastAPI TestClient to test end-to-end RAG,
citations, and fallback behavior.
"""

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- Running Chapter 13 API Verification ---")

# TEST 1: Health
health_resp = client.get("/api/v1/health")
print(f"TEST 1 [Health]: {health_resp.status_code} -> {health_resp.json()}")
assert health_resp.status_code == 200
assert health_resp.json().get("status") == "ok"

# TEST 2: Consumer - Hallmarked Gold
t2_resp = client.post(
    "/api/v1/chat",
    json={"message": "How do I verify hallmarked gold?", "mode": "consumer"},
)
t2 = t2_resp.json()
print("\nTEST 2 [Consumer - Hallmarked Gold]:")
print(f"  found_information: {t2.get('found_information')}")
print(f"  answer: {t2.get('answer')}")
print(f"  citations count: {len(t2.get('citations', []))}")
for c in t2.get("citations", []):
    print(f"    [{c['number']}] {c['title']} ({c['source_url']})")

# Verify criteria for Test 2:
assert t2.get("found_information") is True
assert len(t2.get("citations", [])) > 0
ans2 = t2.get("answer", "")
assert "STUB LLM" not in ans2
assert "similarity=" not in ans2
assert "Retrieved sources:" not in ans2
urls2 = [c["source_url"] for c in t2.get("citations", [])]
assert len(urls2) == len(set(urls2)), "Duplicate source cards detected!"

# TEST 3: HUID
t3_resp = client.post(
    "/api/v1/chat",
    json={"message": "What is HUID?", "mode": "consumer"},
)
t3 = t3_resp.json()
print("\nTEST 3 [HUID]:")
print(f"  found_information: {t3.get('found_information')}")
print(f"  answer: {t3.get('answer')}")
print(f"  citations count: {len(t3.get('citations', []))}")

# TEST 4: Standards
t4_resp = client.post(
    "/api/v1/chat",
    json={"message": "How do I find an Indian Standard?", "mode": "consumer"},
)
t4 = t4_resp.json()
print("\nTEST 4 [Standards]:")
print(f"  found_information: {t4.get('found_information')}")
print(f"  answer: {t4.get('answer')}")
print(f"  citations count: {len(t4.get('citations', []))}")

# TEST 5: Out of scope
t5_resp = client.post(
    "/api/v1/chat",
    json={"message": "How do I bake a chocolate cake?", "mode": "consumer"},
)
t5 = t5_resp.json()
print("\nTEST 5 [Out of Scope - Chocolate Cake]:")
print(f"  found_information: {t5.get('found_information')}")
print(f"  answer: {t5.get('answer')}")
print(f"  citations count: {len(t5.get('citations', []))}")
assert t5.get("found_information") is False
assert len(t5.get("citations", [])) == 0
assert "couldn't find enough relevant information" in t5.get("answer", "").lower()

# TEST 6: Industry Mode
t6_resp = client.post(
    "/api/v1/chat",
    json={
        "message": "How can a manufacturer find the applicable Indian Standard?",
        "mode": "industry",
    },
)
t6 = t6_resp.json()
print("\nTEST 6 [Industry Mode]:")
print(f"  found_information: {t6.get('found_information')}")
print(f"  answer: {t6.get('answer')}")
print(f"  citations count: {len(t6.get('citations', []))}")

print("\n--- All Chapter 13 Verification Assertions Passed! ---")
