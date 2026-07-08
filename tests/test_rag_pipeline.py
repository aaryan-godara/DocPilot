"""
Tests for the RAG Pipeline.

Tests the ingestion and query flows with mocked LLM responses
to avoid requiring an API key in CI/testing.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.backend.services.llm_client import Citation, LLMResponse
from app.backend.services.rag_pipeline import RAGPipeline
from app.backend.services.vector_store import RetrievedChunk


# ── Fixtures ─────────────────────────────────────────────────────────
@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a simple test PDF for ingestion testing."""
    try:
        import fitz  # PyMuPDF

        pdf_path = tmp_path / "test_document.pdf"
        doc = fitz.open()

        # Page 1
        page1 = doc.new_page()
        page1.insert_text(
            (72, 72),
            "Machine learning is a branch of artificial intelligence. "
            "It focuses on building systems that learn from data. "
            "These systems improve their performance over time without "
            "being explicitly programmed for every task.",
        )

        # Page 2
        page2 = doc.new_page()
        page2.insert_text(
            (72, 72),
            "Deep learning is a subset of machine learning. "
            "It uses neural networks with multiple layers. "
            "Convolutional neural networks are commonly used for "
            "image recognition tasks.",
        )

        doc.save(str(pdf_path))
        doc.close()

        return pdf_path

    except Exception:
        pytest.skip("PyMuPDF not available for test PDF generation")


@pytest.fixture
def pipeline_with_temp_chroma(tmp_path, monkeypatch):
    """Create a RAG pipeline using a temp ChromaDB directory."""
    monkeypatch.setattr(
        "app.backend.services.vector_store.settings",
        MagicMock(
            chroma_path=tmp_path / "chroma",
            top_k=3,
            log_level="WARNING",
        ),
    )
    return RAGPipeline()


# ── Tests ────────────────────────────────────────────────────────────
class TestRAGPipelineIngestion:
    """Tests for the ingestion flow."""

    def test_ingest_document(self, sample_pdf_path, tmp_path, monkeypatch):
        """ingest_document processes a PDF end-to-end."""
        # Point upload_path and chroma to temp dirs
        monkeypatch.setattr(
            "app.backend.services.rag_pipeline.settings",
            MagicMock(
                upload_path=sample_pdf_path.parent,
                chunk_size=500,
                chunk_overlap=100,
                top_k=3,
                log_level="WARNING",
                chroma_persist_dir=str(tmp_path / "chroma"),
                embedding_model="all-MiniLM-L6-v2",
            ),
        )
        monkeypatch.setattr(
            "app.backend.services.vector_store.settings",
            MagicMock(
                chroma_path=tmp_path / "chroma",
                top_k=3,
                log_level="WARNING",
            ),
        )

        pipeline = RAGPipeline()
        result = pipeline.ingest_document(sample_pdf_path.name)

        assert result.filename == sample_pdf_path.name
        assert result.total_pages == 2
        assert result.total_chunks > 0
        assert result.embeddings_stored > 0
        assert result.processing_time_seconds > 0


class TestRAGPipelineQuery:
    """Tests for the query flow (with mocked LLM)."""

    def test_ask_question_empty_raises(self, pipeline_with_temp_chroma):
        """ask_question with empty string raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            pipeline_with_temp_chroma.ask_question("")

    def test_ask_question_no_docs_raises(self, pipeline_with_temp_chroma):
        """ask_question with no indexed documents raises ValueError."""
        with pytest.raises(ValueError, match="No documents"):
            pipeline_with_temp_chroma.ask_question("What is this about?")

    @patch("app.backend.services.rag_pipeline.LLMClient")
    def test_ask_question_returns_response(
        self,
        mock_llm_class,
        sample_pdf_path,
        tmp_path,
        monkeypatch,
    ):
        """ask_question returns a structured RAGResponse."""
        # Setup mocked LLM
        mock_llm = MagicMock()
        mock_llm.generate_answer.return_value = LLMResponse(
            answer="Machine learning is a branch of AI [Page 1].",
            citations=[
                Citation(page_numbers=[1], source_file="test_document.pdf", chunk_id="test_chunk_0001")
            ],
            model="grok-3-mini",
            tokens_used=42,
            latency_seconds=0.5,
        )
        mock_llm_class.return_value = mock_llm

        # Setup pipeline with temp storage
        monkeypatch.setattr(
            "app.backend.services.rag_pipeline.settings",
            MagicMock(
                upload_path=sample_pdf_path.parent,
                chunk_size=500,
                chunk_overlap=100,
                top_k=3,
                log_level="WARNING",
                chroma_persist_dir=str(tmp_path / "chroma"),
                embedding_model="all-MiniLM-L6-v2",
            ),
        )
        monkeypatch.setattr(
            "app.backend.services.vector_store.settings",
            MagicMock(
                chroma_path=tmp_path / "chroma",
                top_k=3,
                log_level="WARNING",
            ),
        )

        pipeline = RAGPipeline()

        # Ingest first
        pipeline.ingest_document(sample_pdf_path.name)

        # Force the mocked LLM
        pipeline._llm = mock_llm

        # Ask
        response = pipeline.ask_question("What is machine learning?")

        assert response.answer is not None
        assert len(response.answer) > 0
        assert "machine learning" in response.answer.lower()
        assert response.model == "grok-3-mini"
        assert response.tokens_used == 42
        assert response.processing_time_seconds > 0
        assert len(response.source_chunks) > 0


class TestRAGPipelineEdgeCases:
    """Edge case tests."""

    def test_ingest_nonexistent_file_raises(self, pipeline_with_temp_chroma, monkeypatch):
        """Ingesting a non-existent file raises FileNotFoundError."""
        monkeypatch.setattr(
            "app.backend.services.rag_pipeline.settings",
            MagicMock(
                upload_path=Path(tempfile.mkdtemp()),
                chunk_size=500,
                chunk_overlap=100,
                top_k=3,
                log_level="WARNING",
            ),
        )

        pipeline = RAGPipeline()

        with pytest.raises(FileNotFoundError):
            pipeline.ingest_document("nonexistent.pdf")
