"""
DocPilot — Embedding Service

Generates vector embeddings from text using Sentence Transformers.
Uses the 'all-MiniLM-L6-v2' model by default (384-dimensional vectors).
The model is loaded lazily on first use to avoid startup delays.
"""

from sentence_transformers import SentenceTransformer

from app.backend.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)


class EmbeddingService:
    """
    Generate vector embeddings for text using Sentence Transformers.

    The model is loaded lazily on the first call to avoid slow imports.
    All subsequent calls reuse the cached model instance.

    Args:
        model_name: Name of the Sentence Transformer model to use.

    Example:
        service = EmbeddingService()
        vectors = service.embed_texts(["Hello world", "How are you?"])
        query_vec = service.embed_query("What is this about?")
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model
        self._model: SentenceTransformer | None = None

    def _load_model(self) -> SentenceTransformer:
        """Load the Sentence Transformer model (lazy, one-time)."""
        if self._model is None:
            logger.info(
                "🧠 Loading embedding model: %s (first-time download may take a minute)",
                self.model_name,
            )
            self._model = SentenceTransformer(self.model_name)
            logger.info(
                "✅ Embedding model loaded — dimension: %d",
                self._model.get_sentence_embedding_dimension(),
            )
        return self._model

    @property
    def dimension(self) -> int:
        """Return the embedding dimension of the loaded model."""
        return self._load_model().get_sentence_embedding_dimension()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (each a list of floats).
        """
        if not texts:
            return []

        model = self._load_model()
        logger.info("📐 Embedding %d text(s)...", len(texts))

        embeddings = model.encode(texts, show_progress_bar=False)

        # Convert numpy arrays to plain Python lists
        result = [emb.tolist() for emb in embeddings]

        logger.info("✅ Generated %d embeddings (dim=%d)", len(result), len(result[0]))
        return result

    def embed_query(self, query: str) -> list[float]:
        """
        Generate an embedding for a single query string.

        Args:
            query: The query text to embed.

        Returns:
            A single embedding vector as a list of floats.
        """
        if not query.strip():
            raise ValueError("Query text cannot be empty.")

        model = self._load_model()
        embedding = model.encode(query, show_progress_bar=False)
        return embedding.tolist()
