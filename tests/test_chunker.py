"""
Tests for the text chunking service.

Tests chunk generation, page-number tracking across boundaries,
and configurable chunk size / overlap behavior.
"""

from pathlib import Path

import pytest

from app.backend.services.chunker import DocumentChunk, TextChunker, chunk_document
from app.backend.services.pdf_parser import PageContent


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture
def sample_pages() -> list[PageContent]:
    """Create a list of PageContent objects with known text."""
    return [
        PageContent(
            page_number=1,
            text="Introduction. " * 50,  # ~700 chars
            char_count=len("Introduction. " * 50),
        ),
        PageContent(
            page_number=2,
            text="Methodology details. " * 50,  # ~1050 chars
            char_count=len("Methodology details. " * 50),
        ),
        PageContent(
            page_number=3,
            text="Conclusion and results. " * 50,  # ~1200 chars
            char_count=len("Conclusion and results. " * 50),
        ),
    ]


@pytest.fixture
def short_pages() -> list[PageContent]:
    """Pages with short text that fits in a single chunk."""
    return [
        PageContent(page_number=1, text="Hello world.", char_count=12),
        PageContent(page_number=2, text="Goodbye world.", char_count=14),
    ]


# ── Tests ─────────────────────────────────────────────────────


class TestTextChunker:
    """Tests for TextChunker.chunk_pages()."""

    def test_produces_chunks(self, sample_pages: list[PageContent]) -> None:
        """Should produce at least one chunk from multi-page input."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        assert len(chunks) > 0

    def test_chunk_ids_are_unique(self, sample_pages: list[PageContent]) -> None:
        """Every chunk should have a unique chunk_id."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_id_format(self, sample_pages: list[PageContent]) -> None:
        """chunk_id should follow the '{stem}_chunk_{index}' format."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="report.pdf")
        assert chunks[0].chunk_id == "report_chunk_0000"

    def test_all_chunks_have_page_numbers(
        self, sample_pages: list[PageContent]
    ) -> None:
        """Every chunk should have at least one page number."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        for chunk in chunks:
            assert len(chunk.page_numbers) >= 1

    def test_page_numbers_are_valid(self, sample_pages: list[PageContent]) -> None:
        """All page numbers in chunks should be within [1, 3]."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        for chunk in chunks:
            for pn in chunk.page_numbers:
                assert 1 <= pn <= 3

    def test_chunk_text_is_nonempty(self, sample_pages: list[PageContent]) -> None:
        """No chunk should have empty text."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0

    def test_char_count_matches(self, sample_pages: list[PageContent]) -> None:
        """char_count field should match len(text)."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        for chunk in chunks:
            assert chunk.char_count == len(chunk.text)

    def test_source_file_preserved(self, sample_pages: list[PageContent]) -> None:
        """source_file metadata should match what was passed in."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="my_doc.pdf")
        for chunk in chunks:
            assert chunk.source_file == "my_doc.pdf"

    def test_smaller_chunk_size_produces_more_chunks(
        self, sample_pages: list[PageContent]
    ) -> None:
        """Reducing chunk_size should produce more chunks."""
        large = TextChunker(chunk_size=1000, chunk_overlap=100)
        small = TextChunker(chunk_size=300, chunk_overlap=50)
        large_chunks = large.chunk_pages(sample_pages, source_filename="test.pdf")
        small_chunks = small.chunk_pages(sample_pages, source_filename="test.pdf")
        assert len(small_chunks) > len(large_chunks)

    def test_short_text_single_chunk(self, short_pages: list[PageContent]) -> None:
        """Very short input should produce a single chunk."""
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk_pages(short_pages, source_filename="short.pdf")
        assert len(chunks) == 1

    def test_empty_pages_returns_empty(self) -> None:
        """Empty page list should return no chunks."""
        chunker = TextChunker()
        chunks = chunker.chunk_pages([], source_filename="empty.pdf")
        assert chunks == []

    def test_returns_document_chunk_instances(
        self, sample_pages: list[PageContent]
    ) -> None:
        """Each result should be a DocumentChunk dataclass."""
        chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        chunks = chunker.chunk_pages(sample_pages, source_filename="test.pdf")
        assert all(isinstance(c, DocumentChunk) for c in chunks)


class TestChunkDocumentConvenience:
    """Tests for the chunk_document() convenience function."""

    def test_convenience_function_works(
        self, sample_pages: list[PageContent]
    ) -> None:
        """chunk_document() should produce valid chunks."""
        chunks = chunk_document(
            sample_pages,
            source_filename="test.pdf",
            chunk_size=500,
            chunk_overlap=100,
        )
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)
