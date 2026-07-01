"""
DocPilot — PDF Processing Endpoint

Runs the parse → chunk pipeline on an already-uploaded PDF.
Returns a summary of extracted pages and generated chunks.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.backend.config import get_settings
from app.backend.services.chunker import DocumentChunk, TextChunker
from app.backend.services.pdf_parser import PDFParser
from app.utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)


class ChunkPreview(BaseModel):
    """A preview of a single chunk for the API response."""

    chunk_id: str
    page_numbers: list[int]
    char_count: int
    preview: str  # First 200 chars of the chunk text


class ProcessResponse(BaseModel):
    """Response model for the /process endpoint."""

    filename: str
    total_pages: int
    total_chunks: int
    chunk_size: int
    chunk_overlap: int
    chunks: list[ChunkPreview]


@router.post("/process/{filename}", response_model=ProcessResponse)
async def process_pdf(filename: str) -> ProcessResponse:
    """
    Process an uploaded PDF: parse text and split into chunks.

    Takes a filename of a PDF already saved in the upload directory,
    extracts text page-by-page, then splits into overlapping chunks
    suitable for embedding.

    Args:
        filename: Name of the PDF file in the upload directory.

    Returns:
        ProcessResponse with page count, chunk count, and chunk previews.

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

    # --- Parse PDF ---
    try:
        parser = PDFParser()
        pages = parser.extract_pages(pdf_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("❌ PDF parsing failed for %s: %s", filename, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse PDF: {str(e)}",
        )

    # --- Chunk text ---
    try:
        chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        chunks: list[DocumentChunk] = chunker.chunk_pages(
            pages, source_filename=filename
        )
    except Exception as e:
        logger.error("❌ Chunking failed for %s: %s", filename, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to chunk document: {str(e)}",
        )

    # --- Build response ---
    chunk_previews = [
        ChunkPreview(
            chunk_id=c.chunk_id,
            page_numbers=c.page_numbers,
            char_count=c.char_count,
            preview=c.text[:200] + ("..." if len(c.text) > 200 else ""),
        )
        for c in chunks
    ]

    logger.info(
        "✅ Processed %s: %d pages → %d chunks",
        filename,
        len(pages),
        len(chunks),
    )

    return ProcessResponse(
        filename=filename,
        total_pages=len(pages),
        total_chunks=len(chunks),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        chunks=chunk_previews,
    )
