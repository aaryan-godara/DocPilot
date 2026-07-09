"""
DocPilot — LLM Client Service (Groq)

Sends prompts to the LLM via the Groq API. The Groq API is
OpenAI SDK-compatible, so we use the `openai` Python package with
base_url set to https://api.groq.com/openai/v1.
"""

import time
from dataclasses import dataclass, field

from openai import OpenAI

from app.backend.config import get_settings
from app.backend.services.vector_store import RetrievedChunk
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)


# ── Prompt template ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You are DocPilot, an accurate and helpful document Q&A assistant.

RULES:
1. Answer the user's question using ONLY the context provided below.
2. If the context does not contain enough information, say so clearly.
3. Cite the page number(s) for every fact you use, formatted as [Page X].
4. If a fact spans multiple pages, cite all of them, e.g. [Pages 3-4].
5. Keep your answer concise but thorough.
6. Do NOT make up information that is not in the context."""


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        pages = ", ".join(str(p) for p in chunk.page_numbers)
        parts.append(
            f"--- Context {i} (Page{'s' if len(chunk.page_numbers) > 1 else ''} {pages}) ---\n"
            f"{chunk.text}"
        )
    return "\n\n".join(parts)


# ── Response dataclass ───────────────────────────────────────────────
@dataclass
class Citation:
    """A citation referencing a source page."""

    page_numbers: list[int] = field(default_factory=list)
    source_file: str = ""
    chunk_id: str = ""


@dataclass
class LLMResponse:
    """Structured response from the LLM."""

    answer: str
    citations: list[Citation] = field(default_factory=list)
    model: str = ""
    tokens_used: int = 0
    latency_seconds: float = 0.0


# ── LLM Client ──────────────────────────────────────────────────────
class LLMClient:
    """
    Send prompts to the LLM via the Groq API and parse responses.

    Uses the OpenAI Python SDK with base_url pointed at Groq's endpoint.
    The prompt includes retrieved context chunks with page metadata so
    the model can generate cited answers.

    Args:
        api_key: Groq API key (defaults to settings.groq_api_key).
        base_url: Groq API base URL (defaults to settings.groq_base_url).
        model: Model name (defaults to settings.llm_model).

    Example:
        client = LLMClient()
        response = client.generate_answer("What is RAG?", retrieved_chunks)
        print(response.answer)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.base_url = base_url or settings.groq_base_url
        self.model = model or settings.llm_model

        if not self.api_key:
            raise ValueError(
                "Groq API key is required. Set GROQ_API_KEY in your .env file. "
                "Get a key at https://console.groq.com/keys"
            )

        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        logger.info(
            "🤖 LLM client ready — model: %s, endpoint: %s",
            self.model,
            self.base_url,
        )

    def generate_answer(
        self,
        question: str,
        context_chunks: list[RetrievedChunk],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """
        Generate an answer to a question using retrieved context chunks.

        Builds a prompt with the context and question, sends it to the LLM,
        and returns a structured response with citations extracted from
        the source chunks.

        Args:
            question: The user's question.
            context_chunks: Retrieved chunks with page metadata.
            temperature: Override the default temperature.
            max_tokens: Override the default max tokens.

        Returns:
            LLMResponse with the answer, citations, and usage metadata.

        Raises:
            ValueError: If question is empty or no context provided.
            RuntimeError: If the API call fails.
        """
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        if not context_chunks:
            raise ValueError("No context chunks provided for answer generation.")

        # Build the user message with context
        context_block = _build_context_block(context_chunks)
        user_message = (
            f"CONTEXT:\n{context_block}\n\n"
            f"QUESTION: {question}\n\n"
            f"Answer the question using only the context above. "
            f"Cite page numbers for every claim."
        )

        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens or settings.llm_max_tokens

        logger.info(
            "💬 Generating answer — model: %s, context chunks: %d, temp: %.1f",
            self.model,
            len(context_chunks),
            temp,
        )

        start = time.time()

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=temp,
                max_tokens=tokens,
            )
        except Exception as e:
            logger.error("❌ LLM API call failed: %s", str(e))
            raise RuntimeError(f"LLM API call failed: {str(e)}") from e

        latency = time.time() - start

        # Extract the answer
        answer_text = response.choices[0].message.content or ""
        tokens_used = response.usage.total_tokens if response.usage else 0

        # Build citations from the source chunks used
        citations = [
            Citation(
                page_numbers=chunk.page_numbers,
                source_file=chunk.source_file,
                chunk_id=chunk.chunk_id,
            )
            for chunk in context_chunks
        ]

        logger.info(
            "✅ Answer generated — %d tokens, %.1fs latency",
            tokens_used,
            latency,
        )

        return LLMResponse(
            answer=answer_text.strip(),
            citations=citations,
            model=self.model,
            tokens_used=tokens_used,
            latency_seconds=round(latency, 2),
        )
