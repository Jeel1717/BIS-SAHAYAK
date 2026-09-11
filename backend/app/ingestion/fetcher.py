"""
BIS Sahayak — URL Fetcher
Phase 6: Ingestion Pipeline

Downloads HTML pages or PDF files from public URLs.
Returns raw bytes + detected content type.
Has timeout, retry, and safe error handling.
"""

import time
import logging
from dataclasses import dataclass
from typing import Literal

import requests

logger = logging.getLogger(__name__)

# Browser-like headers so BIS web server doesn't reject the request
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

ContentKind = Literal["html", "pdf", "unknown"]


@dataclass
class FetchResult:
    url: str
    content: bytes
    kind: ContentKind
    status_code: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status_code == 200


def fetch(url: str, timeout: int = 30, retries: int = 2) -> FetchResult:
    """
    Fetch a URL and return raw bytes with detected content type.

    Args:
        url:      The HTTP/HTTPS URL to fetch.
        timeout:  Request timeout in seconds.
        retries:  Number of retry attempts on transient failure.

    Returns:
        FetchResult — always returns an object; check .ok before using .content.
    """
    last_error: str | None = None

    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                delay = 2 ** attempt  # exponential backoff: 2s, 4s
                logger.info("Retrying %s in %ds (attempt %d)", url, delay, attempt + 1)
                time.sleep(delay)

            response = requests.get(
                url,
                headers=_HEADERS,
                timeout=timeout,
                allow_redirects=True,
            )

            content_type = response.headers.get("Content-Type", "").lower()
            if "pdf" in content_type:
                kind: ContentKind = "pdf"
            elif "html" in content_type or "text" in content_type:
                kind = "html"
            else:
                # Guess from URL extension
                kind = "pdf" if url.lower().endswith(".pdf") else "html"

            if response.status_code != 200:
                last_error = f"HTTP {response.status_code}"
                continue

            logger.info(
                "Fetched %s [%s, %d bytes]", url, kind, len(response.content)
            )
            return FetchResult(
                url=url,
                content=response.content,
                kind=kind,
                status_code=response.status_code,
            )

        except requests.exceptions.Timeout:
            last_error = f"Timeout after {timeout}s"
        except requests.exceptions.ConnectionError as e:
            last_error = f"ConnectionError: {e}"
        except requests.exceptions.RequestException as e:
            last_error = f"RequestException: {e}"

    logger.error("Failed to fetch %s: %s", url, last_error)
    return FetchResult(url=url, content=b"", kind="unknown", status_code=0, error=last_error)
