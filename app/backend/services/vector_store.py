"""
DocPilot — Vector Store Service

Manages ChromaDB for storing and retrieving document chunk embeddings.
Provides persistent storage so embeddings survive server restarts.
"""

from dataclasses import dataclass, field

import chromadb

from app.backend.config import get_settings
from app.backend.services.chunker import DocumentChunk
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)

# ChromaDB collection name for all DocPilot documents
COLLECTION_NAME = "docpilot_documents"


@dataclass
class RetrievedChunk:
    """A chunk retrieved from the vector store with its similarity score."""

    chunk_id: str
    text: str
    page_numbers: list[int] = field(default_factory=list)
    source_file: str = ""
    distance: float = 0.0  # Lower = more similar


class VectorStoreService:
    """
    Store and retrieve document embeddings using ChromaDB.

    Uses a single persistent collection for all documents, with
    metadata filtering to scope queries to specific files when needed.

    Args:
        persist_dir: Directory path for ChromaDB persistent storage.

    Example:
        store = VectorStoreService()
        store.add_chunks(chunks, embeddings)
        results = store.query(query_embedding, top_k=5)
    """

    def __init__(self, persist_dir: str | None = None) -> None:
        persist_path = persist_dir or str(settings.chroma_path)

        logger.info("💾 Initializing ChromaDB at: %s", persist_path)
        self._client = chromadb.PersistentClient(path=persist_path)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )
        logger.info(
            "✅ ChromaDB ready — collection '%s' has %d documents",
            COLLECTION_NAME,
            self._collection.count(),
        )

    @property
    def count(self) -> int:
        """Return the number of documents in the collection."""
        return self._collection.count()

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> int:
        """
        Add document chunks and their embeddings to the vector store.

        Uses upsert so re-processing the same document updates existing entries
        rather than creating duplicates.

        Args:
            chunks: List of DocumentChunk objects with text and metadata.
            embeddings: Corresponding embedding vectors for each chunk.

        Returns:
            Number of chunks added/updated.

        Raises:
            ValueError: If chunks and embeddings lists have different lengths.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings."
            )

        if not chunks:
            logger.warning("⚠️ No chunks to add to vector store.")
            return 0

        logger.info("💾 Upserting %d chunks into ChromaDB...", len(chunks))

        # Prepare data for ChromaDB upsert
        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "source_file": c.source_file,
                "page_numbers": ",".join(str(p) for p in c.page_numbers),
                "char_count": c.char_count,
            }
            for c in chunks
        ]

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(
            "✅ Stored %d chunks — collection now has %d total",
            len(chunks),
            self._collection.count(),
        )
        return len(chunks)

    def query(
        self,
        query_embedding: list[float],
        top_k: int | None = None,
        filename: str | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve the most similar chunks for a query embedding.

        Args:
            query_embedding: The embedding vector for the user's question.
            top_k: Number of results to return (default from settings).
            filename: Optional filter to search only in a specific document.

        Returns:
            List of RetrievedChunk objects ordered by similarity (best first).
        """
        k = top_k or settings.top_k

        # Build optional metadata filter
        where_filter = None
        if filename:
            where_filter = {"source_file": filename}

        logger.info(
            "🔍 Querying top-%d chunks%s...",
            k,
            f" from '{filename}'" if filename else "",
        )

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # Parse results into RetrievedChunk objects
        retrieved: list[RetrievedChunk] = []

        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                page_str = results["metadatas"][0][i].get("page_numbers", "")
                page_nums = [int(p) for p in page_str.split(",") if p.strip()]

                retrieved.append(
                    RetrievedChunk(
                        chunk_id=chunk_id,
                        text=results["documents"][0][i],
                        page_numbers=page_nums,
                        source_file=results["metadatas"][0][i].get("source_file", ""),
                        distance=results["distances"][0][i],
                    )
                )

        logger.info("✅ Retrieved %d chunks", len(retrieved))
        return retrieved

    def delete_document(self, filename: str) -> int:
        """
        Delete all chunks belonging to a specific document.

        Args:
            filename: The source filename whose chunks should be removed.

        Returns:
            Number of chunks deleted.
        """
        # Get all IDs for this document
        results = self._collection.get(
            where={"source_file": filename},
            include=[],
        )

        if not results["ids"]:
            logger.info("No chunks found for '%s' — nothing to delete.", filename)
            return 0

        count = len(results["ids"])
        self._collection.delete(ids=results["ids"])

        logger.info("🗑️ Deleted %d chunks for '%s'", count, filename)
        return count

    def list_documents(self) -> list[str]:
        """Return a list of unique source filenames in the store."""
        results = self._collection.get(include=["metadatas"])

        if not results["metadatas"]:
            return []

        filenames = set()
        for meta in results["metadatas"]:
            if meta and meta.get("source_file"):
                filenames.add(meta["source_file"])

        return sorted(filenames)
