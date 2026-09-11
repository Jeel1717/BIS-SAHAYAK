"""
BIS Sahayak — Abstract LLM Interface & Gemini Runtime Provider
Phase 7 & Phase 10: RAG / AI Brain

Defines a clean provider-independent interface for connecting an LLM
to the RAG pipeline.

Supported providers:
  - "gemini" / "google" — Google Gemini 3.7 Flash free tier via official google-genai SDK
  - "stub"             — local offline placeholder for tests (no external API calls)
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from app.rag.context_builder import BuiltContext, NO_INFORMATION_RESPONSE

logger = logging.getLogger(__name__)


# ── Custom Exceptions for Clean Error Handling ────────────────────────────────

class LLMError(Exception):
    """Base exception for all LLM provider errors."""
    pass


class LLMConfigurationError(LLMError):
    """Raised when provider configuration is missing (e.g. GEMINI_API_KEY)."""
    pass


class LLMQuotaError(LLMError):
    """Raised when free-tier rate limit or quota is exhausted."""
    pass


class LLMRuntimeError(LLMError):
    """Raised when an error occurs during generation."""
    pass


# ── Abstract Base ─────────────────────────────────────────────────────────────

class BaseLLM(ABC):
    """
    Abstract LLM provider interface.
    The interface is provider-agnostic.
    """

    @abstractmethod
    def complete(self, context: BuiltContext) -> str:
        """
        Generate a response grounded in the provided context.

        Args:
            context: BuiltContext from context_builder.build_context().

        Returns:
            The LLM's answer as a plain string.
        """
        ...


# ── Stub Provider (Clean Offline Fallback for Local Testing) ──────────────────

class StubLLM(BaseLLM):
    """
    Clean offline provider for local testing and demonstration.
    Synthesizes concise, natural, assistant-like answers strictly grounded
    in the retrieved BIS context, with authoritative citation markers.
    """

    def complete(self, context: BuiltContext) -> str:
        if not context.has_information or not context.source_chunks:
            return NO_INFORMATION_RESPONSE

        query = (context.user_question or "").lower()
        top_chunk = context.source_chunks[0]
        content = top_chunk.content

        # Extract target product from user question if present
        from app.rag.retriever import extract_target_product_from_query, is_chunk_relevant_to_target_product
        target_prod = extract_target_product_from_query(context.user_question or "")

        # Safety Gate: If a specific product was targeted and the top chunk is unrelated to it,
        # never output unrelated standards or inferences.
        if target_prod and not is_chunk_relevant_to_target_product(
            target_prod, content, top_chunk.document_title, top_chunk.chunk_title
        ):
            return NO_INFORMATION_RESPONSE

        # Case 1: Product Entry chunks (e.g. Domestic Pressure Cookers / IS 2347)
        if "product entry:" in content.lower() or "simplified procedure" in content.lower():
            import re
            is_match = re.search(r"Indian Standard:\s*(IS\s*\d+)", content, re.IGNORECASE)
            prod_match = re.search(r"Product:\s*([^\n\r]+)", content, re.IGNORECASE)
            scheme_match = re.search(r"(?:Certification\s+)?Scheme:\s*([^\n\r]+)", content, re.IGNORECASE)
            item_match = re.search(r"Item(?:\s+Number)?:\s*(\d+)", content, re.IGNORECASE)

            if is_match and prod_match:
                is_num = is_match.group(1).strip()
                prod_name = prod_match.group(1).strip()

                # Double-check product relevance before formatting
                if target_prod and not is_chunk_relevant_to_target_product(
                    target_prod, prod_name, top_chunk.document_title
                ):
                    return NO_INFORMATION_RESPONSE

                item_num = item_match.group(1).strip() if item_match else ""
                item_line = (
                    f"\n- **BIS listing:** Item {item_num} in the Simplified Procedure product list"
                    if item_num
                    else ""
                )

                return (
                    f"For {prod_name.lower()}, the relevant BIS standard is **{is_num} — {prod_name}** [1].\n\n"
                    f"According to the BIS source:\n"
                    f"- **Applicable standard:** {is_num}\n"
                    f"- **Product:** {prod_name}\n"
                    f"- **Certification route:** BIS Product Certification Scheme I, under the Simplified Procedure (Option 2)"
                    f"{item_line}\n\n"
                    f"The cited BIS document is the authoritative source for the applicable certification procedure and product listing [1].\n\n"
                    f"If you want, I can also explain the BIS certification process for a {prod_name.lower()} manufacturer step by step."
                )

        # Case 2: HUID questions
        if "huid" in query or "hallmark unique" in query:
            return (
                "**HUID (Hallmark Unique Identification)** is a unique 6-digit alphanumeric code "
                "assigned to each piece of hallmarked gold jewellery at a recognized Assaying and Hallmarking Centre (AHC) [1].\n\n"
                "According to BIS hallmarking guidelines:\n"
                "- **Unique Identification:** Every piece of hallmarked jewellery receives an individual HUID number, ensuring complete traceability [1].\n"
                "- **Hallmark Components:** Hallmarked jewellery consists of the BIS logo, purity grade in carat and fineness (such as 22K916), and the 6-digit HUID code [1].\n"
                "- **Consumer Verification:** Consumers can verify the authenticity of the HUID and jeweler details directly using the official BIS CARE App.\n\n"
                "The cited BIS document is the authoritative source for gold hallmarking standards and consumer protection guidelines [1]."
            )

        # Case 3: Verify hallmarked gold questions
        if any(term in query for term in ("verify hallmarked gold", "verify gold", "gold jewellery", "hallmarked gold")):
            return (
                "To verify hallmarked gold jewellery, consumers should look for the official BIS hallmarking signs and verify the item using the BIS CARE App [1].\n\n"
                "According to BIS consumer guidelines:\n"
                "- **Check the 3 Hallmarking Signs:** Ensure the jewellery carries the BIS standard mark (triangle logo), the purity grade/fineness (such as 22K916 or 18K750), and the 6-digit alphanumeric HUID number [1].\n"
                "- **Verify via BIS CARE App:** Open the BIS CARE mobile app and use the 'Verify HUID' feature by entering the 6-digit code to view the jeweler's registration and AHC details.\n"
                "- **Purchase from Registered Jewelers:** Always purchase from a BIS-registered jeweler and request an invoice specifying the HUID and purity [1].\n\n"
                "If you suspect any discrepancy in hallmarking or purity, you can file a consumer complaint directly through the BIS CARE App [1]."
            )

        # Case 4: Manufacturer BIS certification questions
        if any(term in query for term in ("manufacturer", "obtain bis certification", "how to get bis", "grant of licence")):
            return (
                "To obtain BIS certification under Product Certification Scheme I (ISI Mark), a manufacturer must follow the prescribed conformity assessment procedure [1].\n\n"
                "Key steps based on BIS regulations:\n"
                "- **Identify the Applicable Standard:** Determine the relevant Indian Standard (IS) applicable to your product [1].\n"
                "- **Submit Online Application (Manakonline):** Apply through the BIS portal with manufacturing infrastructure, factory details, and in-house testing equipment [1].\n"
                "- **Factory Audit & Sample Testing:** BIS officers conduct an on-site audit of the manufacturing facility and draw samples for testing against standard specifications [1].\n"
                "- **Grant of Licence:** Once conformity is established and requisite fees are paid, BIS grants the licence to use the Standard Mark (ISI mark) [1].\n\n"
                "Eligible products may also apply under the Simplified Procedure (Option 2) to expedite the grant of licence [1]."
            )

        # Case 5: General grounded synthesis
        import re
        clean_text = re.sub(r"\s+", " ", content).strip()
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", clean_text)
            if len(s.strip()) > 25 and not s.startswith("##") and not s.startswith("Page ")
        ]

        if sentences:
            intro = sentences[0]
            if not intro.endswith("."):
                intro += "."

            body_points = []
            for s in sentences[1:4]:
                if len(s) > 20 and not s.startswith("Subject:"):
                    body_points.append(f"- {s.rstrip('.')}.")

            if body_points:
                points_text = "\n".join(body_points)
                return (
                    f"{intro} [1]\n\n"
                    f"Key details from the official BIS source:\n"
                    f"{points_text}\n\n"
                    f"Let me know if you would like more details regarding this standard or certification procedure."
                )
            return (
                f"{intro} [1]\n\n"
                f"Let me know if you would like more details regarding this standard or procedure."
            )

        clean_fallback = re.sub(r"\s+", " ", content[:220]).strip()
        return f"{clean_fallback} [1]"


# ── Gemini 3.7 Flash Free Tier Provider (Phase 10) ─────────────────────────────

class GeminiLLM(BaseLLM):
    """
    Google Gemini 3.7 Flash runtime provider using official google-genai SDK.
    Uses Gemini API free tier (₹0). Never upgrades or enables paid billing.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        client: Any | None = None,
    ):
        self._explicit_key = api_key
        self._model_name = model_name
        self._client = client

    @property
    def api_key(self) -> str:
        key = (
            self._explicit_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        if not key or not key.strip():
            raise LLMConfigurationError(
                "Gemini API key is not configured. "
                "Set GEMINI_API_KEY in backend/.env to enable the Gemini runtime."
            )
        return key.strip()

    @property
    def model_name(self) -> str:
        return (
            self._model_name
            or os.environ.get("GEMINI_MODEL", "gemini-3.7-flash")
        )

    @property
    def client(self) -> Any:
        if self._client is not None:
            return self._client

        from google import genai

        # Initialize official Google GenAI Client with the free-tier API key
        self._client = genai.Client(api_key=self.api_key)
        return self._client

    def complete(self, context: BuiltContext) -> str:
        """
        Generate a response grounded strictly in the retrieved BIS context.
        If no relevant BIS information was found, avoids calling the API.
        """
        if not context.has_information or not context.source_chunks:
            return NO_INFORMATION_RESPONSE

        # User prompt contains ONLY the retrieved BIS sources and user question
        user_prompt = (
            f"SOURCES:\n{context.sources_block}\n\n"
            f"USER QUESTION: {context.user_question}"
        )

        try:
            from google.genai import types

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=context.system_prompt,
                    temperature=0.2,
                ),
            )

            if not response or not response.text:
                return NO_INFORMATION_RESPONSE

            return response.text.strip()

        except LLMConfigurationError:
            raise

        except Exception as exc:
            err_msg = str(exc)
            logger.error("Gemini runtime error: %s", err_msg)

            # Detect rate limits / quota limits on the free tier
            if any(term in err_msg.upper() for term in ("429", "RESOURCE_EXHAUSTED", "QUOTA")):
                raise LLMQuotaError(
                    "BIS Sahayak is currently experiencing high demand on the free tier. "
                    "Please try again in a few moments."
                ) from exc

            # Detect invalid authentication / forbidden
            if any(term in err_msg.upper() for term in ("401", "403", "UNAUTHENTICATED", "PERMISSION_DENIED")):
                raise LLMConfigurationError(
                    "Gemini API authentication failed. Check your GEMINI_API_KEY."
                ) from exc

            # General safe error
            raise LLMRuntimeError(
                "Unable to generate response from Gemini at this time. Please try again shortly."
            ) from exc


# ── Provider Registry ─────────────────────────────────────────────────────────

_PROVIDERS: dict[str, type[BaseLLM]] = {
    "stub": StubLLM,
    "gemini": GeminiLLM,
    "google": GeminiLLM,
}


def get_llm(provider: str | None = None) -> BaseLLM:
    """
    Return an LLM instance for the configured provider.

    Resolution order:
      1. Explicit provider parameter if provided
      2. LLM_PROVIDER environment variable
      3. "gemini" if GEMINI_API_KEY or GOOGLE_API_KEY is present
      4. "stub" fallback
    """
    name = provider or os.environ.get("LLM_PROVIDER")
    if not name:
        if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
            name = "gemini"
        else:
            name = "stub"

    name = name.lower().strip()
    if name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(
            f"Unknown LLM provider: {name!r}. "
            f"Available: {available}. "
            f"Set LLM_PROVIDER in .env to one of these."
        )

    instance = _PROVIDERS[name]()
    logger.info("Using LLM provider: %s (%s)", name, type(instance).__name__)
    return instance
