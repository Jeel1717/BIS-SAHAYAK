"""
BIS Sahayak — FastAPI Backend
Phase 4: Project Foundation (health endpoint only)
"""

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
# CORS — allow local development and production Vercel origins
# ---------------------------------------------------------------------------
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://bis-sahayak-psi.vercel.app",
    "https://bis-sahayak.vercel.app",
]
_allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
_extra_origins = [
    origin.strip()
    for origin in _allowed_origins_env.split(",")
    if origin.strip() and origin.strip() != "*"
]
_allowed_origins = list(dict.fromkeys(_default_origins + _extra_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure unhandled internal errors return JSON and retain CORS headers."""
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
        # Let FastAPI/Starlette handle standard HTTP errors and validation errors natively
        raise exc

    import logging
    logging.getLogger("uvicorn.error").exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
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

