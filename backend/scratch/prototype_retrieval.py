import os, sys, re
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
from app.rag.embedder import embed_text
from sqlalchemy import text

# Domain entities definition
DOMAIN_ENTITIES = [
    {
        "name": "pressure_cooker",
        "patterns": [
            r"\b(?:pressure\s+)?cooker[s]?\b",
            r"\bpressure\s+cooking\b",
            r"\bis\s*2347\b",
            r"\bis\s*7466\b",
        ],
        "expansion": "pressure cooker Domestic Pressure Cookers IS 2347 IS 7466 Rubber Gaskets",
        "keywords": ["pressure cooker", "pressure cookers", "cooker", "cookers", "is 2347", "is:2347", "is 7466", "domestic pressure cooker"],
        "standards": ["IS 2347", "IS 7466", "2347"],
        "preferred_titles": ["Simplified Procedure", "Scheme I", "Scheme - I"],
    },
    {
        "name": "gold_hallmarking",
        "patterns": [
            r"\b(?:gold|jewellery|jewelry|hallmark(?:ed|ing)?|huid|ahc|carat|karat)\b",
            r"\bis\s*1417\b",
            r"\bis\s*2112\b",
        ],
        "expansion": "hallmarking hallmarked gold jewellery HUID AHC Assaying IS 1417 IS 2112",
        "keywords": ["hallmark", "hallmarked", "hallmarking", "huid", "ahc", "gold", "jewellery", "is 1417", "is 2112"],
        "standards": ["IS 1417", "IS 2112"],
        "preferred_titles": ["Hallmarking", "Jewellers", "Assaying"],
    },
    {
        "name": "isi_mark",
        "patterns": [
            r"\bisi(?:\s+mark(?:ed)?)?\b",
            r"\bscheme\s*(?:-|i|1)\b",
        ],
        "expansion": "ISI mark Scheme I Product Certification Standard Mark conformity",
        "keywords": ["isi mark", "scheme - i", "scheme i", "product certification", "standard mark"],
        "standards": [],
        "preferred_titles": ["Scheme I", "Product Certification"],
    },
    {
        "name": "crs_registration",
        "patterns": [
            r"\bcrs\b",
            r"\bcompulsory\s+registration\b",
            r"\bscheme\s*(?:-|ii|2)\b",
        ],
        "expansion": "CRS Compulsory Registration Scheme Scheme II Self Declaration conformity",
        "keywords": ["crs", "compulsory registration", "scheme - ii", "scheme ii"],
        "standards": [],
        "preferred_titles": ["Scheme II"],
    },
    {
        "name": "complaints",
        "patterns": [
            r"\bcomplaint[s]?\b",
            r"\bgrievance[s]?\b",
        ],
        "expansion": "complaint grievances BIS Certified Products Consumer Protection Guidelines",
        "keywords": ["complaint", "grievances", "consumer protection"],
        "standards": [],
        "preferred_titles": ["Complaints"],
    },
    {
        "name": "laboratory",
        "patterns": [
            r"\blab(?:s|oratory|oratories)?\b",
            r"\blrs\b",
        ],
        "expansion": "Laboratory Recognition Scheme LRS testing outside laboratories",
        "keywords": ["laboratory", "lrs", "testing"],
        "standards": [],
        "preferred_titles": ["Laboratory", "LRS"],
    },
]

def match_entities(query: str):
    q_lower = query.lower()
    matched = []
    for entity in DOMAIN_ENTITIES:
        for pat in entity["patterns"]:
            if re.search(pat, q_lower):
                matched.append(entity)
                break
    return matched

def expand_query(query: str, matched_entities: list) -> str:
    if not matched_entities:
        return query
    expansions = [e["expansion"] for e in matched_entities]
    return f"{query} {' '.join(expansions)}"

def hybrid_retrieve(query: str, db, top_k=5, threshold=0.185):
    matched_entities = match_entities(query)
    expanded_q = expand_query(query, matched_entities)
    
    query_vector = embed_text(expanded_q)
    vec_literal = "[" + ",".join(f"{v:.8f}" for v in query_vector) + "]"
    
    # Collect search keywords for SQL candidate retrieval
    primary_kw = None
    if matched_entities:
        # e.g. for cooker, match %cooker% or %2347%
        entity = matched_entities[0]
        if entity["name"] == "pressure_cooker":
            primary_kw = "%cooker%"
    
    # Candidate search: fetch top semantic matches PLUS any explicit keyword matches
    dist_thresh = 1.0 - threshold
    sql = text("""
        WITH semantic_matches AS (
            SELECT
                c.id          AS chunk_id,
                c.document_id,
                c.content,
                c.chunk_title,
                c.clause_number,
                c.page_number,
                d.title       AS document_title,
                d.standard_number,
                d.document_type,
                d.source_url,
                1 - (c.embedding <=> CAST(:query_vec AS vector)) AS raw_similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
              AND (c.embedding <=> CAST(:query_vec AS vector)) <= :dist_thresh
            ORDER BY c.embedding <=> CAST(:query_vec AS vector)
            LIMIT 30
        ),
        keyword_matches AS (
            SELECT
                c.id          AS chunk_id,
                c.document_id,
                c.content,
                c.chunk_title,
                c.clause_number,
                c.page_number,
                d.title       AS document_title,
                d.standard_number,
                d.document_type,
                d.source_url,
                1 - (c.embedding <=> CAST(:query_vec AS vector)) AS raw_similarity
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
              AND :has_kw = true
              AND (c.content ILIKE :kw OR d.title ILIKE :kw)
            LIMIT 20
        )
        SELECT * FROM semantic_matches
        UNION
        SELECT * FROM keyword_matches
    """)
    
    rows = db.execute(sql, {
        "query_vec": vec_literal,
        "dist_thresh": dist_thresh,
        "has_kw": primary_kw is not None,
        "kw": primary_kw or "",
    }).fetchall()
    
    if not rows:
        return []
    
    # Score and rerank candidates
    scored = []
    q_lower = query.lower()
    query_words = set(re.findall(r"[a-z0-9]+", q_lower)) - {"what", "is", "the", "for", "to", "how", "do", "does", "apply", "applies", "need"}
    
    for row in rows:
        content_lower = row.content.lower()
        doc_title_lower = row.document_title.lower()
        chunk_title_lower = (row.chunk_title or "").lower()
        
        sim = float(row.raw_similarity)
        boost = 0.0
        
        if matched_entities:
            for ent in matched_entities:
                # Check if this chunk is product-specific
                is_product_match = False
                
                # 1. Standard number match (e.g. IS 2347, IS 7466)
                for std in ent["standards"]:
                    if std.lower() in content_lower or (row.standard_number and std.lower() in row.standard_number.lower()):
                        boost += 0.35
                        is_product_match = True
                        if "2347" in std:
                            boost += 0.20  # Extra priority for primary product standard IS 2347
                        if std.lower() in q_lower:
                            boost += 0.20
                        break
                
                # 2. Content keyword match (exact phrase like "pressure cooker")
                for kw in ent["keywords"]:
                    if kw in content_lower:
                        is_product_match = True
                        if kw in ["domestic pressure cooker", "domestic pressure cookers"]:
                            boost += 0.35
                        elif " " in kw:
                            boost += 0.25
                        else:
                            boost += 0.15
                        break
                
                # 3. Preferred document title
                for pref in ent["preferred_titles"]:
                    if pref.lower() in doc_title_lower or pref.lower() in chunk_title_lower:
                        if "simplified procedure" in pref.lower() and is_product_match:
                            boost += 0.25  # High priority for product list specifications
                        else:
                            boost += 0.12
                        break
                
                # 4. Product-specific query vs generic document penalty:
                if ent["name"] == "pressure_cooker":
                    if not is_product_match:
                        boost -= 0.45
                    else:
                        boost += 0.20
        
        final_score = sim + boost
        
        # Only keep if base similarity or boosted score meets threshold
        # (Out of scope queries with zero keyword boost and low sim will stay below threshold)
        if final_score >= threshold:
            scored.append({
                "chunk_id": str(row.chunk_id),
                "document_title": row.document_title,
                "content": row.content,
                "clause_number": row.clause_number,
                "raw_similarity": sim,
                "final_score": final_score,
            })
            
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_k]

s = SessionLocal()
test_cases = [
    "cooker",
    "pressure cooker",
    "cooker certification",
    "what BIS standard applies to pressure cooker",
    "does pressure cooker need BIS certification",
    "What BIS requirements apply to pressure cookers?",
    "what is HUID",
    "how do I verify hallmarked gold",
    "how can a manufacturer obtain BIS certification",
    "how do I bake a chocolate cake",
]

print("\nDETAILED CHECK: 'What BIS requirements apply to pressure cookers?'")
res = hybrid_retrieve("What BIS requirements apply to pressure cookers?", s, top_k=5)
for i, r in enumerate(res, 1):
    print(f"[{i}] Score: {r['final_score']:.4f} (raw: {r['raw_similarity']:.4f}) | Doc: {r['document_title']}")
    print(f"    Excerpt: {r['content'][:140].strip().replace(chr(10), ' ')}...")

