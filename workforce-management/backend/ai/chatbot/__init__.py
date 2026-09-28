"""
AI HR Chatbot Subsystem
-----------------------
Provides natural language conversational HR assistance with grounded RAG,
strict authorization-before-retrieval, MongoDB fact verification,
and Phase 5 AI/ML integration.
"""

from backend.ai.chatbot.router import router

__all__ = ["router"]
