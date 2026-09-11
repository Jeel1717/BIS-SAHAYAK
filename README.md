# BIS Sahayak

> **AI-powered Assistant for Indian Standards and BIS Services**  
> Smart India Hackathon 2026 — Problem Statement **SIH26107**

---

## Table of Contents

1. [What is BIS Sahayak?](#what-is-bis-sahayak)  
2. [Problem Statement — SIH26107](#problem-statement--sih26107)  
3. [Project Structure](#project-structure)  
4. [Technology Stack](#technology-stack)  
5. [Planned Architecture](#planned-architecture)  
6. [Local Development](#local-development)  
7. [Phase Roadmap](#phase-roadmap)  

---

## What is BIS Sahayak?

BIS Sahayak is an intelligent, AI-powered assistant built to help engineers, manufacturers, importers, students, and citizens navigate the complex ecosystem of **Bureau of Indian Standards (BIS)** regulations and Indian Standards (IS) documents.

Instead of manually searching through hundreds of PDF standards or navigating the BIS portal, users can ask natural-language questions and receive accurate, cited answers grounded in official BIS documentation.

---

## Problem Statement — SIH26107

**Organization:** Bureau of Indian Standards (BIS)  
**Theme:** Smart Automation / AI in Governance  

The BIS portal contains thousands of Indian Standard documents, certification guidelines, product regulations, and registration procedures. Searching and interpreting this information is time-consuming for businesses and citizens alike.

The problem demands an AI-based solution that:
- Understands natural-language queries in the context of Indian Standards.
- Retrieves relevant sections from BIS documents accurately.
- Provides clear, cited answers without hallucination.
- Is accessible to both technical and non-technical users.

---

## Project Structure

```
bis-sahayak/
├── frontend/           # Next.js 14 app (TypeScript + Tailwind CSS)
├── backend/            # FastAPI application (Python)
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
├── data/
│   ├── raw_documents/  # Downloaded BIS PDFs (not committed to git)
│   └── processed/      # Chunked, embedded documents (not committed to git)
├── docs/               # Architecture diagrams, meeting notes, research
├── .github/
│   └── workflows/      # CI/CD pipeline definitions (future)
├── .env.example        # Environment variable template
├── .gitignore
└── README.md
```

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| Next.js | 14 | React framework with App Router |
| TypeScript | 5 | Type-safe JavaScript |
| Tailwind CSS | 3 | Utility-first CSS framework |
| React | 18 | UI library |

### Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend language |
| FastAPI | 0.115+ | High-performance async API framework |
| Uvicorn | 0.34+ | ASGI server |

---

## Planned Architecture

> ⚠️ The features below are **planned but not yet implemented**. See the Phase Roadmap section.

### Database — PostgreSQL + pgvector

The production database will be **PostgreSQL** extended with the **pgvector** extension, which enables storing and searching high-dimensional vector embeddings directly in the database.

```
User Question
      │
      ▼
Embed question → vector (1536-dim)
      │
      ▼
pgvector similarity search → top-K relevant document chunks
      │
      ▼
Return chunks + metadata (IS number, section, page)
```

### RAG — Retrieval-Augmented Generation

BIS Sahayak uses a **RAG (Retrieval-Augmented Generation)** pipeline:

```
BIS PDF Documents
      │
      ▼
Text Extraction & Chunking
      │
      ▼
Embedding (OpenAI / Google text-embedding)
      │
      ▼
Store in PostgreSQL + pgvector
      │
      ▼
User Query ──→ Embed ──→ Similarity Search ──→ Retrieve Chunks
                                                      │
                                                      ▼
                                              LLM (GPT / Gemini)
                                                      │
                                                      ▼
                                            Cited Answer to User
```

This approach ensures answers are always **grounded in real BIS documents**, reducing hallucination significantly.

---

## Local Development

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Git

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd bis-sahayak
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 4. Run the Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend runs at: **http://localhost:8000**  
API Docs (auto-generated): **http://localhost:8000/docs**

### 5. Verify the health endpoint

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok",
  "message": "BIS Sahayak backend is running",
  "version": "0.1.0"
}
```

---

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Problem analysis & requirements gathering | ✅ Done |
| Phase 2 | Architecture design & technology selection | ✅ Done |
| Phase 3 | Architecture approval | ✅ Done |
| **Phase 4** | **Project foundation (this phase)** | ✅ **In Progress** |
| Phase 5 | PostgreSQL + pgvector database setup | 🔜 Planned |
| Phase 6 | BIS document ingestion pipeline | 🔜 Planned |
| Phase 7 | RAG pipeline & LLM integration | 🔜 Planned |
| Phase 8 | Chat UI & full frontend | 🔜 Planned |
| Phase 9 | Authentication & user management | 🔜 Planned |
| Phase 10 | Testing, optimization & deployment | 🔜 Planned |

---

## Contributing

This project is developed as part of Smart India Hackathon 2026. For contribution guidelines, see `docs/CONTRIBUTING.md` (coming soon).

---

## License

MIT License — see `LICENSE` for details.
