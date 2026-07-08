"""
DocPilot — PDF Processing Endpoint

Runs the full ingestion pipeline on an already-uploaded PDF:
parse → chunk → embed → store in ChromaDB.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.backend.config import get_settings
from app.backend.services.rag_pipeline import RAGPipeline
from app.utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)

# Shared pipeline instance
_pipeline: RAGPipeline | None = None


def _get_pipeline() -> RAGPipeline:
    """Get or create the shared RAG pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


class ProcessResponse(BaseModel):
    """Response model for the /process endpoint."""

    filename: str
    total_pages: int
    total_chunks: int
    embeddings_stored: int
    chunk_size: int
    chunk_overlap: int
    processing_time_seconds: float


@router.post("/process/{filename}", response_model=ProcessResponse)
async def process_pdf(filename: str) -> ProcessResponse:
    """
    Process an uploaded PDF: parse, chunk, embed, and store.

    Runs the full ingestion pipeline on a PDF already saved in
    the upload directory. After this, the document is ready for
    question answering via the /ask endpoint.

    Args:
        filename: Name of the PDF file in the upload directory.

    Returns:
        ProcessResponse with page count, chunk count, and embeddings stored.

    Raises:
        HTTPException 404: If the file does not exist.
        HTTPException 400: If the file is not a valid PDF.
        HTTPException 500: If processing fails.
    """
    pdf_path = settings.upload_path / filename

    # --- Validate file exists ---
    if not pdf_path.exists():
        logger.warning("File not found for processing: %s", filename)
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {filename}. Upload it first via POST /upload.",
        )

    # --- Run ingestion pipeline ---
    try:
        pipeline = _get_pipeline()
        result = pipeline.ingest_document(filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ Processing failed for %s: %s", filename, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}",
        )

    logger.info(
        "✅ Processed %s: %d pages → %d chunks → %d embeddings",
        filename,
        result.total_pages,
        result.total_chunks,
        result.embeddings_stored,
    )

    return ProcessResponse(
        filename=filename,
        total_pages=result.total_pages,
        total_chunks=result.total_chunks,
        embeddings_stored=result.embeddings_stored,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        processing_time_seconds=result.processing_time_seconds,
    )

