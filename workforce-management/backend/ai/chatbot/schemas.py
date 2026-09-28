"""
Pydantic Schemas for AI HR Chatbot & RAG
----------------------------------------
Data transfer objects for messages, citations, conversation history,
administrative document indexing, and role-based prompt suggestions.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's natural language question or instruction")
    conversation_id: Optional[str] = Field(None, description="Optional ID of active conversation thread. If omitted, a new thread is created.")

class CitationSource(BaseModel):
    title: str = Field(..., description="Descriptive title of source reference")
    source_type: str = Field(..., description="Origin category: 'policy_document', 'database_record', or 'ai_prediction'")
    section: Optional[str] = Field(None, description="Document section or database entity")
    page: Optional[int] = Field(None, description="Document page number where applicable")
    document_name: Optional[str] = Field(None, description="Filename of source policy document")
    snippet: Optional[str] = Field(None, description="Contextual excerpt supporting the answer")

class ChatMessageResponse(BaseModel):
    answer: str = Field(..., description="Grounded answer to user question")
    sources: List[CitationSource] = Field(default_factory=list, description="Citations and evidence origins")
    intent: str = Field(..., description="Classified intent category")
    conversation_id: str = Field(..., description="ID of ongoing conversation thread")
    grounded: bool = Field(True, description="Indicates if answer is strictly backed by verified context")
    timestamp: str = Field(..., description="ISO timestamp of generation")
    follow_up_suggestions: List[str] = Field(default_factory=list, description="Role-relevant follow-up prompt suggestions")

class ConversationMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Text payload of message")
    timestamp: str = Field(..., description="ISO timestamp of message creation")
    intent: Optional[str] = Field(None, description="Intent of message if assistant response")
    sources: List[CitationSource] = Field(default_factory=list, description="Citations attached to message")

class ConversationSummary(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

class ConversationDetail(BaseModel):
    conversation_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ConversationMessage]

class DocumentIndexResponse(BaseModel):
    status: str
    indexed_documents: int
    indexed_chunks: int
    provider: str
    message: str

class SourceDocumentItem(BaseModel):
    document_id: str
    document_name: str
    title: str
    category: str
    file_type: str
    total_pages: int
    chunk_count: int
    indexed_at: str

class SuggestedPromptsResponse(BaseModel):
    role: str
    suggestions: List[str]
