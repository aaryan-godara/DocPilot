"""
DocPilot — Ask Endpoint

Handles question-answering requests using the RAG pipeline.
Embeds the question, retrieves relevant chunks, and generates
an answer with citations via Groq.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.backend.config import get_settings
from app.backend.services.rag_pipeline import RAGPipeline
from app.utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)

# Shared pipeline instance (initialized on first request)
_pipeline: RAGPipeline | None = None


def _get_pipeline() -> RAGPipeline:
    """Get or create the shared RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


# ── Request / Response Models ────────────────────────────────────────
class AskRequest(BaseModel):
    """Request body for the /ask endpoint."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The question to ask about the uploaded document(s).",
        examples=["What is this document about?"],
    )
    filename: str | None = Field(
        default=None,
        description="Optional: restrict the search to a specific uploaded PDF.",
        examples=["report.pdf"],
    )


class CitationResponse(BaseModel):
    """A citation in the answer response."""

    page_numbers: list[int]
    source_file: str
    chunk_id: str


class SourceChunkResponse(BaseModel):
    """A source chunk used to generate the answer."""

    chunk_id: str
    text_preview: str
    page_numbers: list[int]
    source_file: str
    similarity_score: float


class AskResponse(BaseModel):
    """Response from the /ask endpoint."""

    answer: str
    citations: list[CitationResponse]
    source_chunks: list[SourceChunkResponse]
    model: str
    tokens_used: int
    processing_time_seconds: float


# ── Endpoint ─────────────────────────────────────────────────────────
@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    """
    Ask a question about uploaded documents.

    The endpoint embeds the question, retrieves relevant chunks from
    the vector store, and generates an answer with citations using Groq.

    Args:
        request: AskRequest with question and optional filename filter.

    Returns:
        AskResponse with the answer, citations, source chunks, and metadata.

    Raises:
        HTTPException 400: If the question is empty or no documents indexed.
        HTTPException 500: If the pipeline fails.
    """
    logger.info("❓ /ask — question: '%s'", request.question[:100])

    pipeline = _get_pipeline()

    try:
        result = pipeline.ask_question(
            question=request.question,
            filename=request.filename,
        )
    except ValueError as e:
        logger.warning("⚠️ Ask validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error("❌ LLM error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("❌ RAG pipeline error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}",
        )

    return AskResponse(
        answer=result.answer,
        citations=[
            CitationResponse(
                page_numbers=c.page_numbers,
                source_file=c.source_file,
                chunk_id=c.chunk_id,
            )
            for c in result.citations
        ],
        source_chunks=[
            SourceChunkResponse(
                chunk_id=sc.chunk_id,
                text_preview=sc.text_preview,
                page_numbers=sc.page_numbers,
                source_file=sc.source_file,
                similarity_score=sc.similarity_score,
            )
            for sc in result.source_chunks
        ],
        model=result.model,
        tokens_used=result.tokens_used,
        processing_time_seconds=result.processing_time_seconds,
    )
