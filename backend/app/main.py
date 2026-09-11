"""
BIS Sahayak — FastAPI Backend
Phase 4: Project Foundation (health endpoint only)
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="BIS Sahayak API",
    description=(
        "AI-powered Assistant for Indian Standards and BIS Services. "
        "Problem Statement: SIH26107"
    ),
    version="0.1.0",
    docs_url="/docs",          # Swagger UI at /docs
    redoc_url="/redoc",        # ReDoc UI at /redoc
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js frontend (local dev and deployed production)
# ---------------------------------------------------------------------------
_allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
_allowed_origins = [
    origin.strip() for origin in _allowed_origins_env.split(",") if origin.strip()
] or [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if "*" in _allowed_origins:
    _allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
from app.routers import chat_router

app.include_router(chat_router)


@app.get(
    "/api/v1/health",
    summary="Health Check",
    tags=["Health"],
)
async def health_check() -> dict:
    """
    Returns a simple JSON response confirming the backend is running.
    """
    return {
        "status": "ok",
        "message": "BIS Sahayak backend is running",
        "version": "0.1.0",
    }

