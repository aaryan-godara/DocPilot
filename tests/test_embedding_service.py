"""
Tests for the Embedding Service.

Tests embedding generation with Sentence Transformers.
Uses the actual model for integration testing (downloads on first run).
"""

import pytest

from app.backend.services.embedding_service import EmbeddingService


# ── Fixtures ─────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def embedding_service():
    """Create a shared embedding service instance (model loads once)."""
    return EmbeddingService()


# ── Tests ────────────────────────────────────────────────────────────
class TestEmbeddingService:
    """Tests for the EmbeddingService class."""

    def test_embed_single_text(self, embedding_service):
        """embed_texts with a single string returns one vector."""
        result = embedding_service.embed_texts(["Hello world"])

        assert len(result) == 1
        assert isinstance(result[0], list)
        assert all(isinstance(x, float) for x in result[0])

    def test_embed_batch(self, embedding_service):
        """embed_texts with multiple strings returns matching count."""
        texts = ["First text", "Second text", "Third text"]
        result = embedding_service.embed_texts(texts)

        assert len(result) == 3

    def test_embedding_dimension(self, embedding_service):
        """All embeddings have the expected dimension (384 for MiniLM)."""
        result = embedding_service.embed_texts(["Test dimension"])
        expected_dim = embedding_service.dimension

        assert len(result[0]) == expected_dim

    def test_embed_empty_list(self, embedding_service):
        """embed_texts with empty list returns empty list."""
        result = embedding_service.embed_texts([])

        assert result == []

    def test_embed_query(self, embedding_service):
        """embed_query returns a single vector of correct dimension."""
        result = embedding_service.embed_query("What is machine learning?")

        assert isinstance(result, list)
        assert len(result) == embedding_service.dimension
        assert all(isinstance(x, float) for x in result)

    def test_embed_query_empty_raises(self, embedding_service):
        """embed_query with empty string raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            embedding_service.embed_query("")

    def test_embed_query_whitespace_raises(self, embedding_service):
        """embed_query with only whitespace raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            embedding_service.embed_query("   ")

    def test_different_texts_produce_different_embeddings(self, embedding_service):
        """Semantically different texts should produce different embeddings."""
        results = embedding_service.embed_texts([
            "The cat sat on the mat",
            "Quantum physics describes the behavior of particles",
        ])

        # Vectors should not be identical
        assert results[0] != results[1]

    def test_consistent_embeddings(self, embedding_service):
        """Same text should produce the same embedding."""
        text = "Consistency check"
        result1 = embedding_service.embed_query(text)
        result2 = embedding_service.embed_query(text)

        assert result1 == result2

    def test_dimension_property(self, embedding_service):
        """The dimension property returns a positive integer."""
        dim = embedding_service.dimension

        assert isinstance(dim, int)
        assert dim > 0
