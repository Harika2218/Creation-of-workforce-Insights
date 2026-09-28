"""
Indexing Service for RAG Policy Documents
------------------------------------------
Loads HR policy documents, splits them into semantic chunks, generates vector embeddings,
and indexes them into MongoDB collections (rag_documents, rag_chunks, rag_index_metadata).
"""

import os
from typing import Dict, Any, List
from datetime import datetime, timezone

from backend.rag.document_loader import DocumentLoader
from backend.rag.chunker import TextChunker
from backend.rag.embeddings import get_embedding_service, TFIDFEmbeddingService
from backend.rag.vector_store import MongoVectorStore
from database.mongodb import get_db

POLICIES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "policies"
)

class IndexingService:
    """
    Manages indexing and synchronization of enterprise policy documents into the RAG vector store.
    """

    def __init__(self):
        self.vector_store = MongoVectorStore()
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=80)
        self.embedding_service = get_embedding_service()
        self.db = get_db()

    def index_directory(self, dir_path: str = POLICIES_DIR) -> Dict[str, Any]:
        """
        Loads all policy documents in the directory, chunks them, embeds them,
        and saves them to MongoDB.
        """
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Policies directory not found: {dir_path}")

        print(f"[IndexingService] Loading documents from {dir_path}...")
        documents = DocumentLoader.load_directory(dir_path)
        if not documents:
            print("[IndexingService] No supported policy documents found.")
            return {"indexed_documents": 0, "indexed_chunks": 0}

        all_chunks: List[Dict[str, Any]] = []

        # 1. Chunk all documents
        for doc in documents:
            doc_chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(doc_chunks)

            # Upsert document catalog entry
            doc_meta = {
                "document_id": doc["document_id"],
                "document_name": doc["document_name"],
                "title": doc["title"],
                "category": doc["category"],
                "file_type": doc["file_type"],
                "total_pages": doc["total_pages"],
                "total_chunks": len(doc_chunks),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            }
            self.vector_store.upsert_document(doc_meta)

        # 2. Fit TF-IDF on the full corpus if using TFIDFEmbeddingService
        if isinstance(self.embedding_service, TFIDFEmbeddingService):
            corpus_texts = [c["text"] for c in all_chunks]
            self.embedding_service.fit(corpus_texts)

        # 3. Generate embeddings and attach to chunks
        print(f"[IndexingService] Generating vector embeddings for {len(all_chunks)} chunks...")
        texts_to_embed = [c["text"] for c in all_chunks]
        embeddings = self.embedding_service.generate_embeddings(texts_to_embed)

        for chunk, emb in zip(all_chunks, embeddings):
            chunk["embedding"] = emb

        # 4. Save chunks to MongoDB
        self.vector_store.insert_chunks(all_chunks)

        # 5. Record indexing metadata
        self.db.rag_index_metadata.replace_one(
            {"index_name": "hr_policies_vector_index"},
            {
                "index_name": "hr_policies_vector_index",
                "total_documents": len(documents),
                "total_chunks": len(all_chunks),
                "embedding_provider": self.embedding_service.provider_name,
                "embedding_dimension": self.embedding_service.dimension,
                "last_indexed_at": datetime.now(timezone.utc).isoformat(),
                "status": "ready"
            },
            upsert=True
        )

        print(f"[IndexingService] Indexed {len(documents)} documents ({len(all_chunks)} chunks) into MongoDB successfully.")
        return {
            "indexed_documents": len(documents),
            "indexed_chunks": len(all_chunks),
            "provider": self.embedding_service.provider_name,
            "dimension": self.embedding_service.dimension
        }

    def ensure_indexed(self) -> Dict[str, Any]:
        """
        Runs indexing if vector store is currently empty.
        """
        chunk_count = self.db.rag_chunks.count_documents({})
        if chunk_count == 0:
            print("[IndexingService] Vector store empty. Triggering initial policy document indexing...")
            return self.index_directory()
        return {
            "indexed_documents": self.db.rag_documents.count_documents({}),
            "indexed_chunks": chunk_count,
            "status": "already_indexed"
        }
