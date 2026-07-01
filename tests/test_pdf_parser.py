"""
Tests for the PDF parser service.

Tests text extraction from PDFs using PyMuPDF, including
page-level metadata preservation and error handling.
"""

from pathlib import Path

import fitz  # PyMuPDF
import pytest

from app.backend.services.pdf_parser import PDFParser, PageContent, parse_document


# ── Fixtures ──────────────────────────────────────────────────


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a small 3-page PDF for testing."""
    pdf_path = tmp_path / "test_document.pdf"
    doc = fitz.open()

    pages_text = [
        "This is page one of the test document. It contains introductory material.",
        "Page two has more detailed content. This section discusses the methodology.",
        "The third page contains conclusions and references for the study.",
    ]

    for text in pages_text:
        page = doc.new_page(width=612, height=792)  # Letter size
        page.insert_text((72, 72), text, fontsize=12)

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    """Create an empty single-page PDF (no text)."""
    pdf_path = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page(width=612, height=792)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def parser() -> PDFParser:
    return PDFParser()


# ── Tests ─────────────────────────────────────────────────────


class TestPDFParser:
    """Tests for PDFParser.extract_pages()."""

    def test_extracts_correct_page_count(
        self, parser: PDFParser, sample_pdf: Path
    ) -> None:
        """Should extract exactly 3 pages from a 3-page PDF."""
        pages = parser.extract_pages(sample_pdf)
        assert len(pages) == 3

    def test_page_numbers_are_one_indexed(
        self, parser: PDFParser, sample_pdf: Path
    ) -> None:
        """Page numbers should start at 1, not 0."""
        pages = parser.extract_pages(sample_pdf)
        assert pages[0].page_number == 1
        assert pages[1].page_number == 2
        assert pages[2].page_number == 3

    def test_extracted_text_contains_content(
        self, parser: PDFParser, sample_pdf: Path
    ) -> None:
        """Extracted text should contain the words we inserted."""
        pages = parser.extract_pages(sample_pdf)
        assert "introductory" in pages[0].text
        assert "methodology" in pages[1].text
        assert "conclusions" in pages[2].text

    def test_char_count_matches_text_length(
        self, parser: PDFParser, sample_pdf: Path
    ) -> None:
        """char_count field should equal len(text)."""
        pages = parser.extract_pages(sample_pdf)
        for page in pages:
            assert page.char_count == len(page.text)

    def test_returns_page_content_dataclass(
        self, parser: PDFParser, sample_pdf: Path
    ) -> None:
        """Each result should be a PageContent instance."""
        pages = parser.extract_pages(sample_pdf)
        assert all(isinstance(p, PageContent) for p in pages)

    def test_empty_pdf_returns_pages_with_empty_text(
        self, parser: PDFParser, empty_pdf: Path
    ) -> None:
        """An empty PDF should still return page objects (with empty text)."""
        pages = parser.extract_pages(empty_pdf)
        assert len(pages) == 1
        assert pages[0].text.strip() == ""

    def test_file_not_found_raises(self, parser: PDFParser) -> None:
        """Should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            parser.extract_pages(Path("/nonexistent/fake.pdf"))

    def test_non_pdf_extension_raises(
        self, parser: PDFParser, tmp_path: Path
    ) -> None:
        """Should raise ValueError for non-.pdf files."""
        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("not a pdf")
        with pytest.raises(ValueError, match="Not a PDF"):
            parser.extract_pages(txt_file)


class TestParseDocumentConvenience:
    """Tests for the parse_document() convenience function."""

    def test_convenience_function_works(self, sample_pdf: Path) -> None:
        """parse_document() should return the same result as the class."""
        pages = parse_document(sample_pdf)
        assert len(pages) == 3
        assert pages[0].page_number == 1
