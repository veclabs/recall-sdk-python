"""
LangChain integration for Recall by VecLabs.

Usage:
    from langchain_openai import OpenAIEmbeddings
    from solvec.langchain import RecallVectorStore

    store = RecallVectorStore(
        api_key="vl_live_...",
        collection="langchain-memory",
        embeddings=OpenAIEmbeddings(),
    )

    store.add_texts(["User prefers dark mode", "Meeting at 3pm"])
    docs = store.similarity_search("user preferences", k=3)
"""
from __future__ import annotations

import hashlib
import uuid
from typing import Any, Iterable, List, Optional, Sequence, Tuple, Type

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from .client import SolVec


class RecallVectorStore(VectorStore):
    """
    LangChain VectorStore backed by Recall.

    Every write produces a SHA-256 Merkle root.
    On Pro and above, vectors are stored permanently on Arweave via Irys
    and the Merkle root is posted to Solana on every write.
    """

    def __init__(
        self,
        api_key: str,
        collection: str,
        embeddings: Embeddings,
        dimensions: int = 1536,
        metric: str = "cosine",
        api_url: str = "https://api.veclabs.xyz",
    ) -> None:
        self._embeddings = embeddings
        self._collection_name = collection
        self._sv = SolVec(api_key=api_key, api_url=api_url)
        self._collection = self._sv.collection(collection, dimensions=dimensions)

    # ── Required VectorStore interface ──────────────────────────────────────

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Embed texts and upsert into Recall."""
        texts_list = list(texts)
        if not texts_list:
            return []

        embeddings = self._embeddings.embed_documents(texts_list)
        metadatas = metadatas or [{} for _ in texts_list]
        ids = ids or [str(uuid.uuid4()) for _ in texts_list]

        records = []
        for id_, text, embedding, metadata in zip(ids, texts_list, embeddings, metadatas):
            records.append({
                "id": id_,
                "values": embedding,
                "metadata": {**metadata, "text": text},
            })

        self._collection.upsert(records)
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Search for documents similar to query."""
        docs_and_scores = self.similarity_search_with_score(query, k=k, filter=filter)
        return [doc for doc, _ in docs_and_scores]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Search and return documents with relevance scores."""
        query_embedding = self._embeddings.embed_query(query)
        results = self._collection.query(
            vector=query_embedding,
            top_k=k,
        )

        docs_and_scores = []
        for match in results.matches:
            metadata = match.metadata or {}
            text = metadata.pop("text", "")
            doc = Document(page_content=text, metadata=metadata)
            docs_and_scores.append((doc, match.score))

        return docs_and_scores

    @classmethod
    def from_texts(
        cls: Type[RecallVectorStore],
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        api_key: str = "",
        collection: str = "langchain",
        dimensions: int = 1536,
        **kwargs: Any,
    ) -> RecallVectorStore:
        """Create a RecallVectorStore from a list of texts."""
        store = cls(
            api_key=api_key,
            collection=collection,
            embeddings=embedding,
            dimensions=dimensions,
        )
        store.add_texts(texts, metadatas=metadatas)
        return store

    # ── Optional but useful ─────────────────────────────────────────────────

    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Add Document objects directly."""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas=metadatas, ids=ids)

    @property
    def embeddings(self) -> Optional[Embeddings]:
        return self._embeddings

    def verify(self) -> dict:
        """Verify collection integrity against on-chain Merkle root."""
        return self._collection.verify().__dict__