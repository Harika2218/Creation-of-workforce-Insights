"""
Embedding Service Abstraction for RAG
--------------------------------------
Provides a clean, pluggable interface for vector embedding generation.
Supports zero-dependency local TF-IDF vectorization and OpenAI embeddings.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.config import settings

class EmbeddingService(ABC):
    """
    Abstract interface for generating text embeddings.
    """
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generates a dense vector representation for a single string."""
        pass

    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vector representations for a list of strings."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the embedding vector dimension."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name identifier."""
        pass

class TFIDFEmbeddingService(EmbeddingService):
    """
    Local, deterministic TF-IDF embedding service.
    Fast, zero cost, completely offline, and ideal for local policy retrieval.
    """
    DEFAULT_DIMENSION = 512

    def __init__(self, max_features: int = 512):
        self._dimension = max_features
        self._vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self._is_fitted = False
        # Seed vocabulary with domain-specific terms so single-word queries work immediately
        seed_corpus = [
            "leave policy annual privilege casual sick maternity paternity bereavement comp off encashment balance accrual notice period",
            "attendance work hours check in check out grace period late arrival early departure biometric geofencing regularization",
            "remote work hybrid wfh schedule anchor days equipment stipend allowance internet reimbursement vpn security",
            "shift schedule timings morning afternoon general night shift allowance weekend overtime rates 1.5x 2.0x rest breaks fatigue",
            "code of conduct business ethics workplace harassment posh discrimination conflict of interest confidentiality whistleblower",
            "performance management appraisal cycle kpi goals ratings 1.0 2.0 3.0 4.0 5.0 pip performance improvement plan 60 days",
            "learning development training allowance reimbursement 50000 mandatory compliance posh gdpr certifications aws azure",
            "payroll salary pay day last business day payslip components basic hra pf tax deductions insurance mediclaim gmc gpa",
            "faq frequently asked questions notice period 60 days resignation medical certificate healthcare medi card provident fund"
        ]
        self._vectorizer.fit(seed_corpus)
        self._is_fitted = True

    def fit(self, corpus: List[str]):
        """Fits vocabulary on full document collection."""
        if corpus:
            self._vectorizer.fit(corpus)
            self._is_fitted = True

    def generate_embedding(self, text: str) -> List[float]:
        if not text.strip():
            return [0.0] * self._dimension
        vec = self._vectorizer.transform([text]).toarray()[0]
        # Pad or truncate to self._dimension
        padded = np.zeros(self._dimension)
        padded[:len(vec)] = vec
        norm = np.linalg.norm(padded)
        if norm > 0:
            padded = padded / norm
        return padded.tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vecs = self._vectorizer.transform(texts).toarray()
        results = []
        for v in vecs:
            padded = np.zeros(self._dimension)
            padded[:len(v)] = v
            norm = np.linalg.norm(padded)
            if norm > 0:
                padded = padded / norm
            results.append(padded.tolist())
        return results

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def provider_name(self) -> str:
        return "local_tfidf"

class OpenAIEmbeddingService(EmbeddingService):
    """
    OpenAI API Embedding Service using text-embedding-3-small or configured model.
    """
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        if not api_key:
            raise ValueError(
                "OpenAIEmbeddingService requires a valid LLM_API_KEY or OPENAI_API_KEY in environment variables."
            )
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            self._dimension = 1536
        except ImportError:
            raise ImportError("openai package is required for OpenAIEmbeddingService.")

    def generate_embedding(self, text: str) -> List[float]:
        clean_text = text.replace("\n", " ").strip()
        if not clean_text:
            return [0.0] * self._dimension
        response = self.client.embeddings.create(input=[clean_text], model=self.model)
        return response.data[0].embedding

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        clean_texts = [t.replace("\n", " ").strip() or " " for t in texts]
        response = self.client.embeddings.create(input=clean_texts, model=self.model)
        return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def provider_name(self) -> str:
        return f"openai/{self.model}"

# Global singleton instance
_embedding_service_instance: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """
    Factory function returning the configured embedding service.
    Falls back gracefully to TFIDFEmbeddingService if OpenAI is unconfigured.
    """
    global _embedding_service_instance
    if _embedding_service_instance is not None:
        return _embedding_service_instance

    provider = settings.EMBEDDING_PROVIDER.lower()
    api_key = settings.LLM_API_KEY

    if provider == "openai" and api_key:
        try:
            _embedding_service_instance = OpenAIEmbeddingService(
                api_key=api_key,
                model=settings.EMBEDDING_MODEL
            )
            return _embedding_service_instance
        except Exception as e:
            print(f"[EmbeddingService WARN] Failed to initialize OpenAI embeddings ({e}). Falling back to local TF-IDF.")

    # Default fallback
    _embedding_service_instance = TFIDFEmbeddingService()
    return _embedding_service_instance
