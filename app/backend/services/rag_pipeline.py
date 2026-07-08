"""
DocPilot — RAG Pipeline Orchestrator

Wires together the full Retrieval-Augmented Generation pipeline:
  - Ingestion:  PDF → Parse → Chunk → Embed → Store
  - Query:      Question → Embed → Retrieve → LLM → Answer + Citations
"""

import time
from dataclasses import dataclass, field

from app.backend.config import get_settings
from app.backend.services.chunker import DocumentChunk, TextChunker
from app.backend.services.embedding_service import EmbeddingService
from app.backend.services.llm_client import Citation, LLMClient, LLMResponse
from app.backend.services.pdf_parser import PDFParser
from app.backend.services.vector_store import RetrievedChunk, VectorStoreService
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)


# ── Response dataclass ───────────────────────────────────────────────
@dataclass
class SourceChunk:
    """A source chunk included in the RAG response for transparency."""

    chunk_id: str
    text_preview: str  # First 200 chars
    page_numbers: list[int] = field(default_factory=list)
    source_file: str = ""
    similarity_score: float = 0.0


@dataclass
class RAGResponse:
    """Full response from the RAG pipeline."""

    answer: str
    citations: list[Citation] = field(default_factory=list)
    source_chunks: list[SourceChunk] = field(default_factory=list)
    model: str = ""
    tokens_used: int = 0
    processing_time_seconds: float = 0.0


@dataclass
class IngestionResult:
    """Result of the document ingestion pipeline."""

    filename: str
    total_pages: int
    total_chunks: int
    embeddings_stored: int
    processing_time_seconds: float = 0.0


# ── RAG Pipeline ─────────────────────────────────────────────────────
class RAGPipeline:
    """
    Orchestrate document ingestion and question answering.

    Manages the lifecycle of embedding, vector storage, and LLM
    components. Provides two main flows:

    1. ingest_document() — Parse, chunk, embed, and store a PDF.
    2. ask_question() — Retrieve relevant context and generate an answer.

    Example:
        pipeline = RAGPipeline()
        pipeline.ingest_document("report.pdf")
        response = pipeline.ask_question("What are the key findings?")
    """

    def __init__(self) -> None:
        self._embedder = EmbeddingService()
        self._vector_store = VectorStoreService()
        self._parser = PDFParser()
        self._chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        # LLM client is created lazily (requires API key)
        self._llm: LLMClient | None = None

    def _get_llm(self) -> LLMClient:
        """Lazily initialize the LLM client."""
        if self._llm is None:
            self._llm = LLMClient()
        return self._llm

    @property
    def vector_store(self) -> VectorStoreService:
        """Expose the vector store for direct access (e.g., listing docs)."""
        return self._vector_store

    def ingest_document(self, filename: str) -> IngestionResult:
        """
        Run the full ingestion pipeline on an uploaded PDF.

        Flow: PDF → Parse → Chunk → Embed → Store in ChromaDB

        Args:
            filename: Name of the PDF file in the upload directory.

        Returns:
            IngestionResult with counts and timing.

        Raises:
            FileNotFoundError: If the PDF does not exist.
            ValueError: If the file is not a valid PDF.
        """
        start = time.time()
        pdf_path = settings.upload_path / filename

        logger.info("📥 Starting ingestion pipeline for: %s", filename)

        # Step 1: Parse PDF
        pages = self._parser.extract_pages(pdf_path)
        logger.info("  → Parsed %d pages", len(pages))

        # Step 2: Chunk text
        chunks: list[DocumentChunk] = self._chunker.chunk_pages(
            pages, source_filename=filename
        )
        logger.info("  → Created %d chunks", len(chunks))

        if not chunks:
            logger.warning("⚠️ No chunks generated from '%s'", filename)
            return IngestionResult(
                filename=filename,
                total_pages=len(pages),
                total_chunks=0,
                embeddings_stored=0,
                processing_time_seconds=round(time.time() - start, 2),
            )

        # Step 3: Generate embeddings
        texts = [c.text for c in chunks]
        embeddings = self._embedder.embed_texts(texts)
        logger.info("  → Generated %d embeddings", len(embeddings))

        # Step 4: Store in ChromaDB
        stored = self._vector_store.add_chunks(chunks, embeddings)
        logger.info("  → Stored %d chunks in vector database", stored)

        elapsed = round(time.time() - start, 2)
        logger.info(
            "✅ Ingestion complete for '%s' in %.1fs: %d pages → %d chunks → %d embeddings",
            filename,
            elapsed,
            len(pages),
            len(chunks),
            stored,
        )

        return IngestionResult(
            filename=filename,
            total_pages=len(pages),
            total_chunks=len(chunks),
            embeddings_stored=stored,
            processing_time_seconds=elapsed,
        )

    def ask_question(
        self,
        question: str,
        filename: str | None = None,
    ) -> RAGResponse:
        """
        Answer a question using the RAG pipeline.

        Flow: Embed query → Retrieve top-k chunks → LLM → Answer

        Args:
            question: The user's question.
            filename: Optional — restrict search to a specific document.

        Returns:
            RAGResponse with answer, citations, source chunks, and metadata.

        Raises:
            ValueError: If the question is empty or no documents are indexed.
        """
        start = time.time()

        if not question.strip():
            raise ValueError("Question cannot be empty.")

        # Check that we have documents indexed
        if self._vector_store.count == 0:
            raise ValueError(
                "No documents have been indexed yet. "
                "Upload and process a PDF first."
            )

        logger.info("❓ RAG query: '%s'", question[:100])

        # Step 1: Embed the question
        query_embedding = self._embedder.embed_query(question)

        # Step 2: Retrieve relevant chunks
        retrieved: list[RetrievedChunk] = self._vector_store.query(
            query_embedding=query_embedding,
            top_k=settings.top_k,
            filename=filename,
        )

        if not retrieved:
            return RAGResponse(
                answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
                processing_time_seconds=round(time.time() - start, 2),
            )

        # Step 3: Generate answer with LLM
        llm = self._get_llm()
        llm_response: LLMResponse = llm.generate_answer(question, retrieved)

        # Step 4: Build source chunk previews
        source_chunks = [
            SourceChunk(
                chunk_id=chunk.chunk_id,
                text_preview=chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
                page_numbers=chunk.page_numbers,
                source_file=chunk.source_file,
                similarity_score=round(1 - chunk.distance, 4),  # Convert distance to similarity
            )
            for chunk in retrieved
        ]

        elapsed = round(time.time() - start, 2)

        logger.info(
            "✅ RAG response generated in %.1fs — %d tokens used",
            elapsed,
            llm_response.tokens_used,
        )

        return RAGResponse(
            answer=llm_response.answer,
            citations=llm_response.citations,
            source_chunks=source_chunks,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            processing_time_seconds=elapsed,
        )
