"""
Hybrid Document Retriever for RAG
---------------------------------
Combines semantic dense vector search with term-matching ranking to retrieve
the most relevant HR policy excerpts for grounded question answering.
"""

from typing import List, Dict, Any, Optional
import re
from backend.rag.embeddings import get_embedding_service
from backend.rag.vector_store import MongoVectorStore
from backend.config import settings

class RAGRetriever:
    """
    Retrieves and ranks the top-k document chunks for a given query.
    """

    def __init__(self, vector_store: Optional[MongoVectorStore] = None):
        self.vector_store = vector_store or MongoVectorStore()
        self.embedding_service = get_embedding_service()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant document chunks for the user question.
        Applies term matching re-ranking to boost exact keyword hits (e.g. 'maternity', '15 minutes', 'grace period').
        """
        k = top_k or settings.RAG_TOP_K
        query_clean = query.strip()
        if not query_clean:
            return []

        # 1. Generate query embedding
        query_vector = self.embedding_service.generate_embedding(query_clean)

        # 2. Retrieve candidates via vector similarity
        candidates = self.vector_store.search(
            query_vector=query_vector,
            top_k=k * 2,  # Over-retrieve for re-ranking
            category=category,
            min_similarity=settings.RAG_SIMILARITY_THRESHOLD
        )

        if not candidates:
            return []

        # 3. Hybrid boost: boost score if query keywords appear in section or text
        query_terms = [t.lower() for t in re.findall(r"\b\w{3,}\b", query_clean)]
        for c in candidates:
            text_lower = c["text"].lower()
            section_lower = c["section"].lower()
            keyword_score = 0.0

            for term in query_terms:
                if term in section_lower:
                    keyword_score += 0.08
                elif term in text_lower:
                    keyword_score += 0.03

            # Combined hybrid score
            c["hybrid_score"] = round(c["similarity"] + min(keyword_score, 0.25), 4)

        # Sort by hybrid score
        candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return candidates[:k]
