"""
MongoDB Vector Store for RAG Documents
---------------------------------------
Persists document records, chunk vectors, and structural metadata in MongoDB:
  - rag_documents: Master document catalog
  - rag_chunks: Embedded chunks with vector payloads
  - rag_index_metadata: Index state & provider tracking
Computes high-speed cosine similarity search with optional metadata filtering.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from pymongo import ASCENDING, IndexModel
from database.mongodb import get_db

class MongoVectorStore:
    """
    MongoDB-backed vector store implementing cosine similarity retrieval.
    Works seamlessly on local MongoDB Community without requiring Atlas Vector Search,
    while remaining fully upgradeable to $vectorSearch.
    """

    def __init__(self):
        self.db = get_db()
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Creates required lookup indexes on collections."""
        try:
            self.db.rag_documents.create_indexes([
                IndexModel([("document_id", ASCENDING)], unique=True, name="idx_rag_doc_id_unique"),
                IndexModel([("category", ASCENDING)], name="idx_rag_doc_category")
            ])
            self.db.rag_chunks.create_indexes([
                IndexModel([("chunk_id", ASCENDING)], unique=True, name="idx_rag_chunk_id_unique"),
                IndexModel([("document_id", ASCENDING)], name="idx_rag_chunk_doc_id"),
                IndexModel([("category", ASCENDING)], name="idx_rag_chunk_category")
            ])
        except Exception as e:
            # Non-blocking if indexes already exist
            pass

    def upsert_document(self, doc_meta: Dict[str, Any]):
        """Upserts a document entry in rag_documents."""
        self.db.rag_documents.replace_one(
            {"document_id": doc_meta["document_id"]},
            doc_meta,
            upsert=True
        )

    def insert_chunks(self, chunks: List[Dict[str, Any]]):
        """Inserts or replaces embedded chunks into rag_chunks."""
        if not chunks:
            return
        for chunk in chunks:
            self.db.rag_chunks.replace_one(
                {"chunk_id": chunk["chunk_id"]},
                chunk,
                upsert=True
            )

    def delete_document(self, document_id: str):
        """Deletes a document and all its associated chunks."""
        self.db.rag_documents.delete_one({"document_id": document_id})
        self.db.rag_chunks.delete_many({"document_id": document_id})

    def search(
        self,
        query_vector: List[float],
        top_k: int = 4,
        category: Optional[str] = None,
        min_similarity: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Executes vector search by calculating cosine similarity over stored chunk embeddings.
        Returns top_k most similar chunks sorted descending by similarity score.
        """
        query_filter = {}
        if category:
            query_filter["category"] = category

        cursor = self.db.rag_chunks.find(
            query_filter,
            {
                "_id": 0,
                "chunk_id": 1,
                "document_id": 1,
                "document_name": 1,
                "title": 1,
                "section": 1,
                "page": 1,
                "category": 1,
                "text": 1,
                "embedding": 1
            }
        )

        all_chunks = list(cursor)
        if not all_chunks:
            return []

        q_vec = np.array(query_vector, dtype=float)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        scored_chunks = []
        for ch in all_chunks:
            emb = ch.get("embedding")
            if not emb:
                continue
            c_vec = np.array(emb, dtype=float)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue

            similarity = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            if similarity >= min_similarity:
                # Omit large embedding vector from result
                scored_chunks.append({
                    "chunk_id": ch["chunk_id"],
                    "document_id": ch["document_id"],
                    "document_name": ch["document_name"],
                    "title": ch["title"],
                    "section": ch["section"],
                    "page": ch["page"],
                    "category": ch["category"],
                    "text": ch["text"],
                    "similarity": round(similarity, 4)
                })

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]

    def list_sources(self) -> List[Dict[str, Any]]:
        """Returns catalog of indexed policy documents with chunk counts."""
        docs = list(self.db.rag_documents.find({}, {"_id": 0}))
        for d in docs:
            chunk_count = self.db.rag_chunks.count_documents({"document_id": d["document_id"]})
            d["chunk_count"] = chunk_count
        return docs

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on the vector store index."""
        doc_count = self.db.rag_documents.count_documents({})
        chunk_count = self.db.rag_chunks.count_documents({})
        return {
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "status": "ready" if chunk_count > 0 else "empty"
        }
