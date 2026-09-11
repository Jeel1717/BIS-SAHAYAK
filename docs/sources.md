# BIS Sahayak — Phase 6 Knowledge Base Sources

**Phase:** 6 — BIS Knowledge Base  
**Date Accessed:** 2026-09-10  
**Ingestion Status:** Active

All sources are official BIS government web pages at `bis.gov.in`.  
They are publicly accessible, free to read, and constitute official government public information.

---

## Source 1 — BIS Consumer FAQ

| Field | Value |
|---|---|
| **Title** | BIS Consumer FAQ — Frequently Asked Questions for Consumers |
| **URL** | https://www.bis.gov.in/consumer-overview/for-consumers-faq/ |
| **Source Type** | Official BIS FAQ page |
| **Domain** | bis.gov.in |
| **Document Type** | FAQ |
| **Why Useful** | Covers common consumer questions about BIS certification, ISI mark, product standards, complaints, and consumer rights — directly answerable by our RAG system |
| **Date Accessed** | 2026-09-10 |
| **Licensing** | Government of India public information — no copyright restriction on factual public information |

---

## Source 2 — BIS Hallmarking Consumer Protection

| Field | Value |
|---|---|
| **Title** | BIS Hallmarking — Consumer Protection Guide |
| **URL** | https://www.bis.gov.in/hallmarking-overview/consumer-protection/ |
| **Source Type** | Official BIS consumer guide |
| **Domain** | bis.gov.in |
| **Document Type** | Consumer Guide |
| **Why Useful** | Explains mandatory hallmarking of gold jewellery, HUID (Hallmark Unique Identification), consumer rights regarding purity, compensation procedures, and how to verify hallmarks — a very common consumer query domain |
| **Date Accessed** | 2026-09-10 |
| **Licensing** | Government of India public information |

---

## Source 3 — BIS Know Your Standard

| Field | Value |
|---|---|
| **Title** | BIS Know Your Standard — Public Standards Information |
| **URL** | https://www.bis.gov.in/know-your-standard/ |
| **Source Type** | Official BIS public standards education page |
| **Domain** | bis.gov.in |
| **Document Type** | Standards Information |
| **Why Useful** | Explains what Indian Standards (IS) are, how they are developed, what the ISI mark means, which products require mandatory certification, and how to access standards — foundational knowledge for any BIS query |
| **Date Accessed** | 2026-09-10 |
| **Licensing** | Government of India public information |

---

## Source 4 — About BIS

| Field | Value |
|---|---|
| **Title** | About BIS — Bureau of Indian Standards Overview |
| **URL** | https://www.bis.gov.in/the-bureau/about-bis/ |
| **Source Type** | Official BIS institutional overview |
| **Domain** | bis.gov.in |
| **Document Type** | About BIS |
| **Why Useful** | Provides authoritative description of BIS mandate, functions, roles, and history — useful for grounding the assistant's identity and answering "What is BIS?" type questions |
| **Date Accessed** | 2026-09-10 |
| **Licensing** | Government of India public information |

---

## Notes

- All sources are crawled as plain HTML pages using `requests` + `BeautifulSoup`.
- Navigation menus, headers, footers, and sidebars are stripped before chunking.
- No PDF download or login is required for any of these sources.
- These sources form the **Phase 6 MVP knowledge base**. More sources (IS standard PDFs, product certification lists, etc.) will be added in later phases.
- The `bis.gov.in` website is a government-operated site maintained by BIS. Reading and indexing publicly available pages for an educational/assistive tool is consistent with the government's public information mandate.

## Adding More Sources

To add more sources in a future phase:

1. Open `backend/app/ingestion/sources.py`
2. Add a new `SourceConfig(...)` entry to `BIS_SOURCES`
3. Re-run `python run_ingestion.py` — it will only ingest new sources (existing ones are skipped)
