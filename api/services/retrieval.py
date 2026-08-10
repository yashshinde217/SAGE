from collections import defaultdict

from rank_bm25 import BM25Okapi

from services import vector_store


class HybridRetriever:
    """Combines ChromaDB semantic search with an in-memory BM25 keyword
    index, merged via Reciprocal Rank Fusion (RRF).
    """

    def __init__(self) -> None:
        self._bm25: BM25Okapi | None = None
        self._bm25_ids: list[str] = []
        self._bm25_docs: dict[str, dict] = {}

    def _build_bm25_index(self) -> None:
        """(Re)builds the in-memory BM25 index from everything currently
        stored in ChromaDB. Called lazily and rebuilt each search — cheap
        for small/medium corpora; revisit with a cache-invalidation
        strategy if the corpus grows large.
        """
        collection = vector_store.get_or_create_collection()
        result = collection.get(include=["documents", "metadatas"])

        ids = result["ids"]
        documents = result["documents"]
        metadatas = result["metadatas"]

        self._bm25_ids = ids
        self._bm25_docs = {
            doc_id: {"text": text, "metadata": meta}
            for doc_id, text, meta in zip(ids, documents, metadatas)
        }

        if not documents:
            self._bm25 = None
            return

        tokenized = [doc.lower().split() for doc in documents]
        self._bm25 = BM25Okapi(tokenized)

    def _bm25_search(self, query: str, top_k: int) -> list[str]:
        """Returns a ranked list of chunk ids from BM25, best first."""
        if self._bm25 is None or not self._bm25_ids:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)

        ranked = sorted(
            zip(self._bm25_ids, scores), key=lambda pair: pair[1], reverse=True
        )
        return [doc_id for doc_id, score in ranked[:top_k] if score > 0]

    def _vector_search(self, query: str, top_k: int) -> list[str]:
        """Returns a ranked list of chunk ids from ChromaDB semantic search."""
        results = vector_store.query_similar(query, n_results=top_k)
        ids = results.get("ids", [[]])[0]
        return ids

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        self._build_bm25_index()

        vector_ids = self._vector_search(query, top_k=10)
        bm25_ids = self._bm25_search(query, top_k=10)

        # Reciprocal Rank Fusion: score = 1 / (rank + 60), rank is 0-indexed.
        rrf_scores: dict[str, float] = defaultdict(float)

        for rank, doc_id in enumerate(vector_ids):
            rrf_scores[doc_id] += 1.0 / (rank + 60)

        for rank, doc_id in enumerate(bm25_ids):
            rrf_scores[doc_id] += 1.0 / (rank + 60)

        fused_ids = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
        top_ids = fused_ids[:top_k]

        # BM25 branch is self-sufficient (built from full collection.get()),
        # but vector-only hits won't be in self._bm25_docs if the corpus
        # changed between calls in edge cases — fetch any missing ones directly.
        missing = [doc_id for doc_id in top_ids if doc_id not in self._bm25_docs]
        if missing:
            collection = vector_store.get_or_create_collection()
            fetched = collection.get(ids=missing, include=["documents", "metadatas"])
            for doc_id, text, meta in zip(
                fetched["ids"], fetched["documents"], fetched["metadatas"]
            ):
                self._bm25_docs[doc_id] = {"text": text, "metadata": meta}

        results = []
        for doc_id in top_ids:
            entry = self._bm25_docs.get(doc_id)
            if entry is None:
                continue
            results.append(
                {
                    "chunk_id": doc_id,
                    "text": entry["text"],
                    "source_file": entry["metadata"].get("source_file"),
                    "page_number": entry["metadata"].get("page_number"),
                }
            )

        return results