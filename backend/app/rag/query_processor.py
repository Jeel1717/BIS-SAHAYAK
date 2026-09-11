"""
BIS Sahayak — Domain Query Expansion & Hybrid Scoring Processor
RAG / AI Brain

Provides:
  1. Lightweight domain entity & product intent detection.
  2. Targeted query expansion for vector embedding.
  3. Hybrid relevance scoring: semantic similarity + lexical relevance +
     product standard boost + generic administrative chunk penalty.

Zero-cost, dependency-free (standard library re only).
Does NOT hardcode answers; boosts actual evidence chunks from the knowledge base.
"""

import re
from dataclasses import dataclass, field


@dataclass
class DomainEntity:
    """A domain entity rule for query expansion and retrieval scoring."""
    name: str
    patterns: list[str]
    expansion_terms: str
    content_keywords: list[str]
    standards: list[str]
    preferred_titles: list[str]
    is_product: bool = False


# Reusable Domain Entity Registry
DOMAIN_ENTITIES: list[DomainEntity] = [
    # 1. Domestic Pressure Cookers (IS 2347) & Accessories (IS 7466)
    DomainEntity(
        name="pressure_cooker",
        patterns=[
            r"\b(?:pressure\s+)?cooker[s]?\b",
            r"\bpressure\s+cooking\b",
            r"\bis\s*2347\b",
            r"\bis\s*7466\b",
        ],
        expansion_terms="pressure cooker Domestic Pressure Cookers IS 2347 IS 7466 Rubber Gaskets",
        content_keywords=[
            "domestic pressure cooker",
            "domestic pressure cookers",
            "pressure cooker",
            "pressure cookers",
            "cooker",
            "cookers",
            "is 2347",
            "is:2347",
            "is 7466",
        ],
        standards=["IS 2347", "IS 7466", "2347", "7466"],
        preferred_titles=["Simplified Procedure", "Scheme I", "Scheme - I"],
        is_product=True,
    ),
    # 2. Gold & Silver Hallmarking, HUID & AHC (IS 1417 & IS 2112)
    DomainEntity(
        name="gold_hallmarking",
        patterns=[
            r"\b(?:gold|jewellery|jewelry|hallmark(?:ed|ing)?|huid|ahc|carat|karat)\b",
            r"\bis\s*1417\b",
            r"\bis\s*2112\b",
            r"\bis\s*15820\b",
        ],
        expansion_terms="hallmarking hallmarked gold jewellery HUID AHC Assaying IS 1417 IS 2112",
        content_keywords=[
            "hallmark",
            "hallmarked",
            "hallmarking",
            "huid",
            "ahc",
            "gold",
            "jewellery",
            "is 1417",
            "is 2112",
        ],
        standards=["IS 1417", "IS 2112", "IS 15820"],
        preferred_titles=["Hallmarking", "Jewellers", "Assaying", "AHC"],
        is_product=False,
    ),
    # 3. ISI Mark & Product Certification Scheme I
    DomainEntity(
        name="isi_mark",
        patterns=[
            r"\bisi(?:\s+mark(?:ed)?)?\b",
            r"\bscheme\s*(?:-|i|1)\b",
        ],
        expansion_terms="ISI mark Scheme I Product Certification Standard Mark conformity",
        content_keywords=["isi mark", "scheme - i", "scheme i", "product certification", "standard mark"],
        standards=[],
        preferred_titles=["Scheme I", "Product Certification"],
        is_product=False,
    ),
    # 4. Compulsory Registration Scheme (CRS) / Scheme II
    DomainEntity(
        name="crs_registration",
        patterns=[
            r"\bcrs\b",
            r"\bcompulsory\s+registration\b",
            r"\bscheme\s*(?:-|ii|2)\b",
        ],
        expansion_terms="CRS Compulsory Registration Scheme Scheme II Self Declaration conformity",
        content_keywords=["crs", "compulsory registration", "scheme - ii", "scheme ii"],
        standards=[],
        preferred_titles=["Scheme II"],
        is_product=False,
    ),
    # 5. Consumer Complaints & Grievances
    DomainEntity(
        name="complaints",
        patterns=[
            r"\bcomplaint[s]?\b",
            r"\bgrievance[s]?\b",
            r"\bdefect(?:ive)?\b",
        ],
        expansion_terms="complaint grievances BIS Certified Products Consumer Protection Guidelines",
        content_keywords=["complaint", "grievances", "consumer protection", "penalty"],
        standards=[],
        preferred_titles=["Complaints"],
        is_product=False,
    ),
    # 6. Testing & Laboratory Recognition Scheme (LRS)
    DomainEntity(
        name="laboratory",
        patterns=[
            r"\blab(?:s|oratory|oratories)?\b",
            r"\blrs\b",
            r"\btesting\s+facilit(?:y|ies)\b",
        ],
        expansion_terms="Laboratory Recognition Scheme LRS testing outside laboratories",
        content_keywords=["laboratory", "lrs", "testing", "samples"],
        standards=[],
        preferred_titles=["Laboratory", "LRS"],
        is_product=False,
    ),
    # 7. Indian Standards & Standards Formulation
    DomainEntity(
        name="standards",
        patterns=[
            r"\bindian\s+standard[s]?\b",
            r"\bknow\s+your\s+standard\b",
            r"\bkys\b",
            r"\bstandard\s+formulation\b",
        ],
        expansion_terms="Indian Standard Know Your Standard formulation Technical Committee",
        content_keywords=["indian standard", "know your standard", "standard"],
        standards=[],
        preferred_titles=["Handbook", "Standards", "Know Your Standard"],
        is_product=False,
    ),
]


def detect_domain_entities(query: str) -> list[DomainEntity]:
    """Detect matching domain entities based on natural language query patterns."""
    q_lower = query.lower()
    matched = []
    for entity in DOMAIN_ENTITIES:
        for pat in entity.patterns:
            if re.search(pat, q_lower):
                matched.append(entity)
                break
    return matched


def expand_query_for_embedding(query: str, matched_entities: list[DomainEntity]) -> str:
    """Enrich query with domain expansion terms before generating semantic embedding."""
    if not matched_entities:
        return query
    expansions = [e.expansion_terms for e in matched_entities]
    return f"{query} {' '.join(expansions)}"


def extract_primary_keyword(matched_entities: list[DomainEntity]) -> str | None:
    """Extract primary SQL ILIKE keyword pattern for candidate retrieval, if applicable."""
    if not matched_entities:
        return None
    for entity in matched_entities:
        if entity.name == "pressure_cooker":
            return "%cooker%"
    return None


def calculate_hybrid_score(
    raw_similarity: float,
    content: str,
    doc_title: str,
    chunk_title: str | None,
    standard_number: str | None,
    query: str,
    matched_entities: list[DomainEntity],
) -> float:
    """
    Compute hybrid score combining semantic similarity and domain relevance.
    
    Formula:
      final_score = raw_similarity
                  + standard_boost
                  + content_keyword_boost
                  + title_preference_boost
                  - generic_penalty (for product queries when chunk is generic)
    """
    score = raw_similarity
    if not matched_entities:
        return score

    content_lower = content.lower()
    doc_title_lower = doc_title.lower()
    chunk_title_lower = (chunk_title or "").lower()
    q_lower = query.lower()

    boost = 0.0

    for ent in matched_entities:
        is_product_match = False

        # 1. Standard number match (e.g. IS 2347, IS 1417)
        for std in ent.standards:
            if std.lower() in content_lower or (standard_number and std.lower() in standard_number.lower()):
                boost += 0.35
                is_product_match = True
                # Primary product standard extra priority (e.g. IS 2347 for cookers)
                if "2347" in std:
                    boost += 0.20
                if std.lower() in q_lower:
                    boost += 0.20
                break

        # 2. Content keyword match (exact phrase like "pressure cooker")
        for kw in ent.content_keywords:
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
        for pref in ent.preferred_titles:
            if pref.lower() in doc_title_lower or pref.lower() in chunk_title_lower:
                if "simplified procedure" in pref.lower() and is_product_match:
                    boost += 0.25
                else:
                    boost += 0.12
                break

        # 4. Product-specific query vs generic document penalty
        if ent.is_product:
            if not is_product_match:
                # Penalize generic administrative chunks (e.g. central government powers)
                # when the user specifically asked about a concrete product.
                boost -= 0.45
            else:
                boost += 0.20

            # Focused chunk title bonus: prioritizes chunks dedicated to this product/standard
            if chunk_title_lower:
                for std in ent.standards:
                    if std.lower() in chunk_title_lower:
                        boost += 0.30
                        break
                for kw in ent.content_keywords:
                    if kw in chunk_title_lower:
                        boost += 0.25
                        break

            # Multi-standard catalog penalty: demote giant table/compilation chunks
            # that list 3 or more distinct Indian Standards when searching for a single product
            distinct_standards = set(re.findall(r"\bIS\s+\d+", content))
            if len(distinct_standards) >= 3:
                boost -= 0.60

    return score + boost
