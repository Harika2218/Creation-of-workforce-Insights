"""
RAG (Retrieval-Augmented Generation) Subsystem for InnovateCorp HR Assistant
-----------------------------------------------------------------------------
Provides multi-format document loading, structural text chunking, embedding
generation, vector store search, and hybrid context retrieval.
"""

from backend.rag.document_loader import DocumentLoader
from backend.rag.chunker import TextChunker
from backend.rag.embeddings import get_embedding_service, EmbeddingService
from backend.rag.vector_store import MongoVectorStore
from backend.rag.retriever import RAGRetriever
from backend.rag.indexing_service import IndexingService

__all__ = [
    "DocumentLoader",
    "TextChunker",
    "get_embedding_service",
    "EmbeddingService",
    "MongoVectorStore",
    "RAGRetriever",
    "IndexingService",
]
