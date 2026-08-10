from functools import lru_cache
from typing import Any

import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer

from config import get_settings

settings = get_settings()

COLLECTION_NAME = "sage_documents"


class NomicEmbeddingFunction(EmbeddingFunction):
    """Wraps nomic-embed-text-v1.5 for use as a ChromaDB embedding function.

    Nomic models require a task-specific prefix. We index with
    'search_document: ' since this function is used at ingestion time.
    Query-time embedding uses a separate 'search_query: ' prefix — see
    embed_query() below.
    """

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            settings.embedding_model_name,
            trust_remote_code=True,
        )

    def __call__(self, input: Documents) -> Embeddings:
        prefixed = [f"search_document: {text}" for text in input]
        return self.model.encode(prefixed, convert_to_numpy=True).tolist()

    def embed_query(self, query: str) -> list[float]:
        prefixed = f"search_query: {query}"
        return self.model.encode([prefixed], convert_to_numpy=True)[0].tolist()


@lru_cache
def get_embedding_function() -> NomicEmbeddingFunction:
    # Cached so the model loads into memory once per process, not per request.
    return NomicEmbeddingFunction()


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def get_or_create_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(
    ids: list[str],
    texts: list[str],
    metadatas: list[dict[str, Any]],
) -> None:
    collection = get_or_create_collection()
    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)


def query_similar(query_text: str, n_results: int = 5) -> dict[str, Any]:
    collection = get_or_create_collection()
    query_embedding = get_embedding_function().embed_query(query_text)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )


def get_stats() -> dict[str, Any]:
    collection = get_or_create_collection()
    count = collection.count()
    # Distinct source files among stored metadata
    if count > 0:
        all_meta = collection.get(include=["metadatas"])["metadatas"]
        sources = {m.get("source_file") for m in all_meta if m.get("source_file")}
    else:
        sources = set()
    return {
        "total_vectors": count,
        "indexed_documents": len(sources),
        "source_files": sorted(sources),
    }