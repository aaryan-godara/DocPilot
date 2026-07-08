"""
Tests for the Vector Store Service (ChromaDB).

Uses a temporary directory for ChromaDB storage so tests don't
affect the real database.
"""

import tempfile

import pytest

from app.backend.services.chunker import DocumentChunk
from app.backend.services.embedding_service import EmbeddingService
from app.backend.services.vector_store import VectorStoreService


# ── Fixtures ─────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def embedding_service():
    """Shared embedding service (model loads once per test module)."""
    return EmbeddingService()


@pytest.fixture
def vector_store(tmp_path):
    """Create a fresh vector store with a temp directory for each test."""
    return VectorStoreService(persist_dir=str(tmp_path / "chroma_test"))


@pytest.fixture
def sample_chunks():
    """Create sample document chunks for testing."""
    return [
        DocumentChunk(
            chunk_id="test_chunk_0001",
            text="Machine learning is a subset of artificial intelligence.",
            page_numbers=[1],
            source_file="test.pdf",
            char_count=55,
        ),
        DocumentChunk(
            chunk_id="test_chunk_0002",
            text="Deep learning uses neural networks with many layers.",
            page_numbers=[1, 2],
            source_file="test.pdf",
            char_count=51,
        ),
        DocumentChunk(
            chunk_id="test_chunk_0003",
            text="Photosynthesis is the process by which plants convert sunlight.",
            page_numbers=[3],
            source_file="test.pdf",
            char_count=62,
        ),
    ]


@pytest.fixture
def sample_chunks_other_doc():
    """Chunks from a different document for multi-doc testing."""
    return [
        DocumentChunk(
            chunk_id="other_chunk_0001",
            text="Python is a popular programming language.",
            page_numbers=[1],
            source_file="other.pdf",
            char_count=40,
        ),
    ]


# ── Tests ────────────────────────────────────────────────────────────
class TestVectorStoreService:
    """Tests for the VectorStoreService class."""

    def test_initial_count_is_zero(self, vector_store):
        """A new vector store should have zero documents."""
        assert vector_store.count == 0

    def test_add_chunks(self, vector_store, sample_chunks, embedding_service):
        """add_chunks stores the correct number of chunks."""
        texts = [c.text for c in sample_chunks]
        embeddings = embedding_service.embed_texts(texts)

        stored = vector_store.add_chunks(sample_chunks, embeddings)

        assert stored == 3
        assert vector_store.count == 3

    def test_add_empty_chunks(self, vector_store):
        """add_chunks with empty list returns zero."""
        stored = vector_store.add_chunks([], [])

        assert stored == 0

    def test_add_mismatched_raises(self, vector_store, sample_chunks):
        """add_chunks with mismatched lengths raises ValueError."""
        with pytest.raises(ValueError, match="Mismatch"):
            vector_store.add_chunks(sample_chunks, [[0.1, 0.2]])

    def test_query_returns_results(self, vector_store, sample_chunks, embedding_service):
        """Querying after adding chunks returns relevant results."""
        texts = [c.text for c in sample_chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store.add_chunks(sample_chunks, embeddings)

        query_emb = embedding_service.embed_query("What is machine learning?")
        results = vector_store.query(query_emb, top_k=2)

        assert len(results) == 2
        # The most relevant chunk should be about ML
        assert "machine learning" in results[0].text.lower() or "artificial intelligence" in results[0].text.lower()

    def test_query_top_k(self, vector_store, sample_chunks, embedding_service):
        """Query respects the top_k parameter."""
        texts = [c.text for c in sample_chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store.add_chunks(sample_chunks, embeddings)

        query_emb = embedding_service.embed_query("Tell me something")
        results = vector_store.query(query_emb, top_k=1)

        assert len(results) == 1

    def test_query_returns_metadata(self, vector_store, sample_chunks, embedding_service):
        """Query results include correct metadata."""
        texts = [c.text for c in sample_chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store.add_chunks(sample_chunks, embeddings)

        query_emb = embedding_service.embed_query("machine learning")
        results = vector_store.query(query_emb, top_k=1)

        assert len(results) == 1
        assert results[0].source_file == "test.pdf"
        assert len(results[0].page_numbers) > 0
        assert results[0].chunk_id.startswith("test_chunk_")

    def test_query_with_filename_filter(
        self,
        vector_store,
        sample_chunks,
        sample_chunks_other_doc,
        embedding_service,
    ):
        """Query with filename filter only returns chunks from that document."""
        all_chunks = sample_chunks + sample_chunks_other_doc
        texts = [c.text for c in all_chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store.add_chunks(all_chunks, embeddings)

        query_emb = embedding_service.embed_query("programming")
        results = vector_store.query(query_emb, top_k=5, filename="other.pdf")

        assert all(r.source_file == "other.pdf" for r in results)

    def test_upsert_updates_existing(self, vector_store, embedding_service):
        """Upserting a chunk with the same ID updates instead of duplicating."""
        chunk_v1 = DocumentChunk(
            chunk_id="upsert_test",
            text="Original text content",
            page_numbers=[1],
            source_file="test.pdf",
            char_count=21,
        )
        chunk_v2 = DocumentChunk(
            chunk_id="upsert_test",
            text="Updated text content",
            page_numbers=[1],
            source_file="test.pdf",
            char_count=20,
        )

        emb1 = embedding_service.embed_texts([chunk_v1.text])
        vector_store.add_chunks([chunk_v1], emb1)
        assert vector_store.count == 1

        emb2 = embedding_service.embed_texts([chunk_v2.text])
        vector_store.add_chunks([chunk_v2], emb2)
        assert vector_store.count == 1  # Still 1, not 2

    def test_delete_document(self, vector_store, sample_chunks, embedding_service):
        """delete_document removes all chunks for a specific file."""
        texts = [c.text for c in sample_chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store.add_chunks(sample_chunks, embeddings)

        assert vector_store.count == 3

        deleted = vector_store.delete_document("test.pdf")
        assert deleted == 3
        assert vector_store.count == 0

    def test_delete_nonexistent_document(self, vector_store):
        """delete_document on a non-existent file returns zero."""
        deleted = vector_store.delete_document("nonexistent.pdf")
        assert deleted == 0

    def test_list_documents(self, vector_store, sample_chunks, sample_chunks_other_doc, embedding_service):
        """list_documents returns unique filenames."""
        all_chunks = sample_chunks + sample_chunks_other_doc
        texts = [c.text for c in all_chunks]
        embeddings = embedding_service.embed_texts(texts)
        vector_store.add_chunks(all_chunks, embeddings)

        docs = vector_store.list_documents()
        assert sorted(docs) == ["other.pdf", "test.pdf"]

    def test_list_documents_empty(self, vector_store):
        """list_documents on empty store returns empty list."""
        docs = vector_store.list_documents()
        assert docs == []
