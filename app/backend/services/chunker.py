"""
DocPilot — Text Chunking Service

Splits extracted PDF text into overlapping chunks using LangChain's
RecursiveCharacterTextSplitter. Preserves page-number metadata so
each chunk can be traced back to its source page(s) for citations.
"""

from dataclasses import dataclass, field
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.backend.services.pdf_parser import PageContent
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DocumentChunk:
    """A chunk of text with metadata for retrieval and citation."""

    chunk_id: str  # Unique ID: "{filename}_chunk_{index}"
    text: str
    page_numbers: list[int] = field(default_factory=list)  # Pages this chunk spans
    source_file: str = ""
    char_count: int = 0


class TextChunker:
    """
    Split page-level text into overlapping chunks for embedding.

    Uses LangChain's RecursiveCharacterTextSplitter which tries to
    split on paragraph/sentence boundaries before falling back to
    character-level splits.

    The chunker preserves which page(s) each chunk originated from,
    which is critical for generating citations with page numbers.

    Args:
        chunk_size: Maximum characters per chunk (default 1000).
        chunk_overlap: Overlap between consecutive chunks (default 200).

    Example:
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk_pages(pages, source_filename="report.pdf")
        for chunk in chunks:
            print(f"Chunk {chunk.chunk_id}: pages {chunk.page_numbers}")
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_pages(
        self,
        pages: list[PageContent],
        source_filename: str = "",
    ) -> list[DocumentChunk]:
        """
        Split a list of page contents into overlapping text chunks.

        Each chunk tracks which page(s) it came from. When a chunk
        straddles a page boundary (due to overlap), it lists all
        contributing page numbers.

        Args:
            pages: List of PageContent objects from the PDF parser.
            source_filename: Original PDF filename for metadata.

        Returns:
            A list of DocumentChunk objects ready for embedding.
        """
        if not pages:
            logger.warning("⚠️ No pages provided for chunking.")
            return []

        logger.info(
            "✂️ Chunking %d pages from '%s' (size=%d, overlap=%d)",
            len(pages),
            source_filename,
            self.chunk_size,
            self.chunk_overlap,
        )

        # Build a mapping of character offsets → page numbers.
        # We concatenate all page texts with page-break markers,
        # then track where each page's text starts and ends.
        full_text = ""
        page_ranges: list[tuple[int, int, int]] = []  # (start, end, page_number)

        for page in pages:
            start = len(full_text)
            full_text += page.text
            end = len(full_text)
            page_ranges.append((start, end, page.page_number))

        if not full_text.strip():
            logger.warning("⚠️ All pages are empty in '%s'.", source_filename)
            return []

        # Split the concatenated text into chunks
        text_chunks: list[str] = self._splitter.split_text(full_text)

        # Map each chunk back to its source page(s)
        chunks: list[DocumentChunk] = []
        search_start = 0

        for idx, chunk_text in enumerate(text_chunks):
            # Find where this chunk appears in the full text
            chunk_start = full_text.find(chunk_text, search_start)
            if chunk_start == -1:
                # Fallback: search from the beginning
                chunk_start = full_text.find(chunk_text)
            chunk_end = chunk_start + len(chunk_text)

            # Update search position (allow overlap)
            search_start = max(search_start, chunk_start + 1)

            # Determine which pages this chunk spans
            chunk_pages: list[int] = []
            for p_start, p_end, p_num in page_ranges:
                # Chunk overlaps with this page if they share any characters
                if chunk_start < p_end and chunk_end > p_start:
                    chunk_pages.append(p_num)

            stem = Path(source_filename).stem if source_filename else "doc"
            chunk = DocumentChunk(
                chunk_id=f"{stem}_chunk_{idx:04d}",
                text=chunk_text,
                page_numbers=chunk_pages,
                source_file=source_filename,
                char_count=len(chunk_text),
            )
            chunks.append(chunk)

        logger.info(
            "✅ Created %d chunks from '%s'",
            len(chunks),
            source_filename,
        )

        return chunks


def chunk_document(
    pages: list[PageContent],
    source_filename: str = "",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[DocumentChunk]:
    """
    Convenience function to chunk parsed PDF pages.

    Args:
        pages: List of PageContent from the PDF parser.
        source_filename: Original PDF filename.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between chunks.

    Returns:
        List of DocumentChunk objects.
    """
    chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_pages(pages, source_filename=source_filename)
