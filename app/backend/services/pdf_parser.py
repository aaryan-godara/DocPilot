"""
DocPilot — PDF Parser Service

Extracts text from PDF documents page-by-page using PyMuPDF (fitz).
Preserves page numbers for downstream citation tracking.
"""

from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PageContent:
    """Represents extracted text from a single PDF page."""

    page_number: int  # 1-indexed page number
    text: str
    char_count: int


class PDFParser:
    """
    Parse PDF documents and extract text with page-level metadata.

    Uses PyMuPDF (fitz) for fast, accurate text extraction.
    Each page's text is returned with its page number, enabling
    downstream citation tracking.

    Example:
        parser = PDFParser()
        pages = parser.extract_pages(Path("data/raw/report.pdf"))
        for page in pages:
            print(f"Page {page.page_number}: {page.char_count} chars")
    """

    def extract_pages(self, pdf_path: Path) -> list[PageContent]:
        """
        Extract text from all pages of a PDF document.

        Args:
            pdf_path: Absolute path to the PDF file.

        Returns:
            A list of PageContent objects, one per page.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the file cannot be opened as a PDF.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if not pdf_path.suffix.lower() == ".pdf":
            raise ValueError(f"Not a PDF file: {pdf_path}")

        logger.info("📄 Parsing PDF: %s", pdf_path.name)

        pages: list[PageContent] = []

        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            logger.error("❌ Failed to open PDF '%s': %s", pdf_path.name, str(e))
            raise ValueError(f"Cannot open PDF '{pdf_path.name}': {str(e)}") from e

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")  # Plain text extraction

                page_content = PageContent(
                    page_number=page_num + 1,  # 1-indexed
                    text=text,
                    char_count=len(text),
                )
                pages.append(page_content)

            total_chars = sum(p.char_count for p in pages)
            logger.info(
                "✅ Parsed %d pages (%d total chars) from %s",
                len(pages),
                total_chars,
                pdf_path.name,
            )

        finally:
            doc.close()

        return pages


def parse_document(pdf_path: Path) -> list[PageContent]:
    """
    Convenience function to parse a PDF and return page contents.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of PageContent objects with extracted text.
    """
    parser = PDFParser()
    return parser.extract_pages(pdf_path)
